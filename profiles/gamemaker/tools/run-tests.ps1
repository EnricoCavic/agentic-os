# Runs the GMTL test suite via Igor (headless-style: the game window opens briefly, runs the
# suites, and exits itself). Engine-profile slot 2. Exit code 0 = all tests passed.
#
# Requires GMTL vendored in scripts/GMTL_* with its run-at-start macro wired to GAME_RUN_TESTS
# (see profiles/gamemaker/README.md step 4).
#
# Usage: powershell -ExecutionPolicy Bypass -File tools\run-tests.ps1
param(
    [string]$ProjectDir = (Split-Path $PSScriptRoot -Parent),
    [string]$Runtime = "C:\ProgramData\GameMakerStudio2-LTS2026\Cache\runtimes\runtime-2026.0.0.23",
    [string]$LogPath = "",
    [int]$TimeoutSec = 180
)

$igor = "$Runtime\bin\igor\windows\x64\Igor.exe"
$userDir = Get-ChildItem "$env:APPDATA\GameMakerStudio2-LTS2026" -Directory |
    Where-Object { $_.Name -match '_\d+$' } | Select-Object -First 1 -ExpandProperty FullName
$yyp = Get-ChildItem $ProjectDir -Filter *.yyp | Select-Object -First 1 -ExpandProperty FullName

if (-not (Test-Path $igor)) { Write-Error "Igor.exe not found at $igor (override -Runtime)"; exit 2 }
if (-not $userDir) { Write-Error "No logged-in GameMaker user folder found (open the IDE and log in once)"; exit 2 }
if (-not $yyp) { Write-Error "No .yyp found in $ProjectDir"; exit 2 }

$slug = [IO.Path]::GetFileNameWithoutExtension($yyp) -replace '[^A-Za-z0-9_-]', '_'
if (-not $LogPath) { $LogPath = "$env:TEMP\$slug-tests.log" }

if (Test-Path $LogPath) { Remove-Item $LogPath -Force }
$env:GAME_RUN_TESTS = "1"
$proc = Start-Process -FilePath $igor -ArgumentList @(
    "/project=`"$yyp`"", "/rp=`"$Runtime`"", "/uf=`"$userDir`"",
    "/cache=`"$env:TEMP\gmcache-$slug`"", "/temp=`"$env:TEMP\gmtemp-$slug`"",
    "--", "Windows", "Run"
) -NoNewWindow -PassThru -RedirectStandardOutput $LogPath
$env:GAME_RUN_TESTS = $null

# Watchdog: a GML runtime error opens a blocking dialog; detect and kill.
$elapsed = 0
while (-not $proc.HasExited -and $elapsed -lt $TimeoutSec) {
    Start-Sleep -Seconds 2
    $elapsed += 2
    $c = Get-Content $LogPath -Raw -ErrorAction SilentlyContinue
    if ($c -match 'ERROR!!!') {
        Write-Warning "Runtime error detected; killing game"
        Get-Process -Name Runner -ErrorAction SilentlyContinue | Stop-Process -Force
        break
    }
}
if (-not $proc.HasExited) {
    try { $proc | Wait-Process -Timeout 10 -ErrorAction Stop } catch {
        Get-Process -Name Runner -ErrorAction SilentlyContinue | Stop-Process -Force
        try { $proc | Stop-Process -Force -ErrorAction Stop } catch {}
    }
}

$content = Get-Content $LogPath -Raw -ErrorAction SilentlyContinue
if (-not $content) { Write-Error "No log output produced"; exit 2 }

# Print the GMTL section of the log
$show = $false
foreach ($line in ($content -split "`r?`n")) {
    if ($line -match 'Suite|describe|it\(|Tests Finished|Test Suites:|Tests:|finished in|Skipped|line \d+|Expected|Received') { $show = $true }
    if ($show -and $line.Trim()) { Write-Output $line.Trim() }
    if ($line -match 'tests: complete') { break }
}

$passed = ($content -match 'Tests Finished') -and
          ($content -match 'Tests: \d+ passed') -and
          ($content -notmatch '\d+ failed') -and
          ($content -notmatch 'ERROR!!!')
if ($passed) { Write-Output "`nRESULT: PASS"; exit 0 } else { Write-Output "`nRESULT: FAIL (see $LogPath)"; exit 1 }

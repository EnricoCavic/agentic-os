# Builds and runs the game via Igor (GameMaker LTS). Engine-profile slot 1 (headless build/run)
# and, with -Autopilot, slot 3 (automated smoke run — requires the autopilot pattern wired into
# the game; see profiles/gamemaker/snippets/autopilot.gml).
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File tools\run-game.ps1              # normal play
#   powershell -ExecutionPolicy Bypass -File tools\run-game.ps1 -Autopilot  # self-playing demo
param(
    [switch]$Autopilot,
    [string]$ProjectDir = (Split-Path $PSScriptRoot -Parent),
    [string]$Runtime = "C:\ProgramData\GameMakerStudio2-LTS2026\Cache\runtimes\runtime-2026.0.0.23",
    [string]$LogPath = ""
)

$igor = "$Runtime\bin\igor\windows\x64\Igor.exe"
$userDir = Get-ChildItem "$env:APPDATA\GameMakerStudio2-LTS2026" -Directory |
    Where-Object { $_.Name -match '_\d+$' } | Select-Object -First 1 -ExpandProperty FullName
$yyp = Get-ChildItem $ProjectDir -Filter *.yyp | Select-Object -First 1 -ExpandProperty FullName

if (-not (Test-Path $igor)) { Write-Error "Igor.exe not found at $igor (override -Runtime)"; exit 2 }
if (-not $userDir) { Write-Error "No logged-in GameMaker user folder found (open the IDE and log in once)"; exit 2 }
if (-not $yyp) { Write-Error "No .yyp found in $ProjectDir"; exit 2 }

$slug = [IO.Path]::GetFileNameWithoutExtension($yyp) -replace '[^A-Za-z0-9_-]', '_'
if (-not $LogPath) { $LogPath = "$env:TEMP\$slug-run.log" }

if ($Autopilot) { $env:GAME_AUTOPILOT = "1" } else { $env:GAME_AUTOPILOT = $null }
$env:GAME_RUN_TESTS = $null

Write-Output "Building and running $yyp (log: $LogPath)..."
& $igor /project="$yyp" /rp="$Runtime" /uf="$userDir" /cache="$env:TEMP\gmcache-$slug" /temp="$env:TEMP\gmtemp-$slug" -- Windows Run | Out-File -Encoding utf8 $LogPath
$env:GAME_AUTOPILOT = $null
Write-Output "Game exited (Igor code $LASTEXITCODE). Log: $LogPath"

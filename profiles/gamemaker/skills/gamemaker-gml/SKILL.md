<!-- GameMaker engine-profile skill template. Copy to .agents/skills/gamemaker-gml/SKILL.md -->
<!-- in the downstream project and replace <PROJECT> placeholders (or let /app-init do it). -->

# GameMaker GML & Project-Format Safety

## When to Apply

- **Classification**: ALL (any task touching `.gml`, `.yy`, `.yyp`, sprites, or build tooling)
- **Phase**: /plan, /implement, /review, /test

## Conventions

- **IDE-closed discipline**: no structural edits (`.yyp`, new `.yy`, event-list changes) while the
  GameMaker IDE is open. Verify with `Get-Process | Where-Object { $_.ProcessName -match 'GameMaker' }`.
- **`.yyp` single-writer**: only the primary agent registers assets. Subagents receive
  already-scaffolded `.gml` files and fill content only.
- `.yy`/`.yyp` JSON keeps trailing commas — edit textually, never re-serialize.
- Banned variable names: `score`, `lives`, `health` (legacy GML globals shadow them). Use
  project-specific names instead.
- Event file names encode the event: `Create_0.gml`, `Step_0.gml`, `Alarm_N.gml`, `Draw_64.gml`
  (Draw GUI); each needs a matching `eventList` entry (types 0/3/2/8).
- All tuning values are macros in a single constants script (e.g. `scr_<PROJECT>`) — no magic
  numbers in object events.
- Runtime switches via env vars: `GAME_RUN_TESTS=1` (GMTL at boot, self-exit),
  `GAME_AUTOPILOT=1` (self-playing run + screenshot). See `profiles/gamemaker/snippets/autopilot.gml`.

## Checklist

- [ ] IDE closed before any structural change (process check evidence in Work Log)
- [ ] New assets registered in `.yyp` `resources` (alphabetical) — rooms also in `RoomOrderNodes`
- [ ] No `score`/`lives`/`health` variable names anywhere (`grep -rn` before review)
- [ ] Every failure path logs via `show_debug_message()` (visible in Igor stdout)
- [ ] Compile clean via `tools\run-game.ps1` log; tests pass via `tools\run-tests.ps1` exit 0
- [ ] GMTL tests use `simulateKeyHold`+`simulateFrameWait`, never `simulateKeyPress`

## Anti-Patterns

- Running `.yy` files through strict JSON parsers/formatters (strips trailing commas → IDE churn
  or breakage)
- Creating sprites with a single PNG (needs the duplicate under
  `layers/<frameGUID>/<layerGUID>.png` + GMSequence keyframes)
- Testing input with 1-frame simulated presses (GMTL ticks time sources before stepping instances)
- Killing the Runner process and treating Igor's nonzero exit as a build failure (expected for
  automated stops)
- Parallel agents editing `.yyp` simultaneously (guaranteed corruption)

## References

- `profiles/gamemaker/README.md` (profile overview + install)
- Downstream project's architecture ADR (canonical file-format authority once `/app-init` runs)
- `.agents/skills/doc-lookup/SKILL.md` (GML manual lookup + network caveat)

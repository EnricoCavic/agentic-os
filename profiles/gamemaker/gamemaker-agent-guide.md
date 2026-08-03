# Working with GameMaker as an AI Agent — Field Guide

Everything an AI agent needs to safely build, run, playtest, and modify a GameMaker
project without a human driving the IDE. Distilled from two shipped Playsaurus pilots
(a Flappy Bird evaluation and the "Yeet-stone" fully-agentic demo, 2026), both built
end-to-end through direct file editing + CLI builds with zero project corruption.
Verified on **GameMaker LTS 2026** (IDE 2026.0.0.16, runtime 2026.0.0.23), Windows, VM builds.

---

## 1. The proven stack: direct file editing + Igor CLI

A GameMaker project is plain files: GML source, JSON-like `.yy`/`.yyp` metadata, PNGs.
The proven agent workflow edits those files directly and builds with the **Igor** CLI
bundled inside the runtime. Evaluated alternatives, for the record:

- Official `@gamemaker/gm-cli` — unusable when `gamemaker.io` is unreachable (studio network blocks it).
- Community `gms-mcp` — useful only for symbol indexing; couldn't find the LTS 2026 runtime,
  enforces `o_` naming, and rewrites `.yyp` (dangerous). Do not let any tool re-serialize project files.
- **Direct editing + Igor: no dependencies, full control, proven over two full builds.**

### Raw Igor invocation

```
C:\ProgramData\GameMakerStudio2-LTS2026\Cache\runtimes\runtime-2026.0.0.23\bin\igor\windows\x64\Igor.exe
  /project="<abs path>\<Game>.yyp"
  /rp="C:\ProgramData\GameMakerStudio2-LTS2026\Cache\runtimes\runtime-2026.0.0.23"
  /uf="%APPDATA%\GameMakerStudio2-LTS2026\<user>_<id>"
  /cache="%TEMP%\gmcache-<slug>" /temp="%TEMP%\gmtemp-<slug>"
  -- Windows Run
```

Facts that matter:

- `/uf` needs the per-user folder created by a **one-time IDE login**. If absent, a human must
  open the IDE and log in once; after that the IDE is never needed for builds.
- **Compile errors AND `show_debug_message()` output go to Igor's stdout** — always capture:
  `| Out-File -Encoding utf8 <log>`. This log is the agent's eyes; every failure path in game
  code should `show_debug_message()` so evidence is greppable.
- **A GML runtime error opens a BLOCKING modal dialog** — the game hangs until dismissed.
  The error text is already in the log (marker: `ERROR!!!`). Automated wrappers need a watchdog
  that kills the `Runner` process when the log contains `ERROR!!!`.
- **Killing the Runner makes Igor exit nonzero — that is EXPECTED for automated stops**, not a
  build failure. Judge runs by log content, never by Igor's exit code alone.
- Wrap all of this once per project as `tools/run-game.ps1` and `tools/run-tests.ps1`
  (reference implementations live next to this guide in `profiles/gamemaker/tools/`).

### Runtime switches (environment variables)

Builds stay identical; behavior forks on env vars read at boot
(`environment_get_variable`). Convention: `GAME_RUN_TESTS=1` (test suites at boot,
self-exit) and `GAME_AUTOPILOT=1` (self-playing run). Prefix per project if desired.

### The game's sandbox save dir

`ini_open`, `screen_save`, etc. write to `%LOCALAPPDATA%\<Game_Name>\` (spaces →
underscores). Screenshots and save files land there — that's where evidence gets collected.

---

## 2. The golden rules (violating these corrupts projects)

1. **Close the GameMaker IDE before any structural change** — new assets, `.yyp` edits,
   `.yy` event-list changes. The IDE holds the whole project in memory and silently
   overwrites external edits on its next save. Editing the *contents* of existing `.gml`
   files with the IDE open is safe. Check before structural work:
   `Get-Process | Where-Object { $_.ProcessName -match 'GameMaker' }`.
2. **`.yy`/`.yyp` are JSON with trailing commas everywhere.** Edit them textually,
   preserving style. Never round-trip through a strict JSON parser/serializer — it strips
   the trailing commas and causes IDE churn or breakage.
3. **`.yyp` is a single-writer resource.** In multi-agent work, exactly one agent
   (the coordinator) registers assets; parallel agents only fill `.gml` files that were
   already scaffolded. Two writers on `.yyp` = guaranteed corruption.
4. **The IDE normalizes hand-authored `.yy` on first open** (version tags, key order).
   Harmless — commit that normalization as its own commit and move on.
5. When authoring any new `.yy`, **clone the nearest existing asset of the same type and
   modify it** (fresh GUIDs, new names) rather than writing from scratch — the schema has
   many easy-to-miss required fields.

---

## 3. Project anatomy & asset registration

```
<Game>/
├── <Game>.yyp                  # project manifest — SINGLE-WRITER
├── <Game>.resource_order       # IDE-managed display order (safe to leave alone)
├── objects/obj_*/              # obj_*.yy + one .gml per event (Create_0.gml, Step_0.gml, ...)
├── scripts/scr_*/              # <name>.yy + <name>.gml (functions, macros, enums)
├── sprites/spr_*/              # .yy + TWO identical PNGs per frame (see §7)
├── rooms/Room1/                # Room1.yy (see §6)
├── options/, datafiles/        # platform options, included files
└── tools/                      # Igor wrapper scripts
```

Naming: `obj_`/`scr_`/`spr_` snake_case; functions snake_case prefixed by domain
(`economy_buy()`); macros UPPER_SNAKE_CASE; enums PascalCase type with UPPER members
(`GameState.AIM`).

**Registering a new asset requires BOTH halves:**

1. The asset folder: `type/<name>/<name>.yy` plus payload files (`.gml`, PNGs).
2. An entry in `.yyp` `resources` (keep alphabetical):
   `{"id":{"name":"<name>","path":"<type>/<name>/<name>.yy",},},`
   Rooms additionally need an entry in `.yyp` `RoomOrderNodes`.

**Object events ↔ files ↔ `eventList`:** each event is its own `.gml` file next to the
object's `.yy`, and needs a matching entry in the `.yy` `eventList`:

| File | eventType | eventNum |
|---|---|---|
| `Create_0.gml` | 0 | 0 |
| `Alarm_N.gml` | 2 | N |
| `Step_0.gml` | 3 | 0 |
| `Draw_0.gml` | 8 | 0 |
| `Draw_64.gml` (Draw GUI) | 8 | 64 |

---

## 4. GML language traps (all cost real debugging time)

- **Never name a variable `score`, `lives`, or `health`.** They are legacy *built-in
  globals*; instance assignment silently writes the global, and reading `obj.score` then
  errors "not set before reading it". Use `run_views`, `player_hp`, `best_distance`.
- **Built-in function names can't be variables either** (e.g. `power`) — compile error
  "read-only function". Check the manual/autocomplete namespace before naming.
- **Depth trap:** the default room Background layer sits at depth **100**. Instances at
  depth ≥ 100 draw *behind* it. Keep gameplay/custom-draw depths < 100.
- All tuning values live as macros in one constants script — no magic numbers inside
  object events. This is what lets tests assert against the same constants the game uses.
- Every failure path logs via `show_debug_message()` — Igor stdout is the only place
  an agent can see runtime behavior.

---

## 5. Headless playtesting A: unit/logic tests with GMTL

**GMTL** (github.com/DAndrewBox/GM-Testing-Library, v1.2) — a Jest-style GML test
library. Vendor it by hand into `scripts/GMTL_*` (skip its demo assets).

**Wiring:** in `GMTL_definitions.gml` set:

```gml
#macro gmtl_run_at_start           (environment_get_variable("GAME_RUN_TESTS") == "1")
#macro gmtl_wait_frames_before_start  10
#macro gmtl_show_coverage          false
```

With the env var set, suites run at boot instead of the game and the process exits itself.
Summary line in the log: `Tests: N passed, M total.` — the test wrapper greps for it plus
the absence of `failed` / `ERROR!!!`.

**API shape** (one suite script, e.g. `scripts/scr_game_tests`):

```gml
suite(function() {
    describe("launch math (AC-2)", function() {
        beforeEach(function() { economy_reset(); });
        it("clamps fractions above 1", function() {
            expect(game_launch_velocity(1.5, false, 0)).toBe(game_launch_velocity(1.0, false, 0));
        });
    });
});
```

Matchers seen in production: `.toBe()`, `.toBeTruthy()`, `.toBeFalsy()`, `.toHaveLength()`.
Hooks: `beforeEach`/`afterEach`/`beforeAll`/`afterAll`.

**Hard-won GMTL rules:**

- **Use `simulateKeyHold` + `simulateFrameWait` + `simulateKeyRelease`, never
  `simulateKeyPress`.** GMTL ticks its simulated time sources BEFORE stepping instances,
  so a 1-frame press is cleared before any Step event reads it.
- GMTL redefines `keyboard_check*`/`mouse_check*` project-wide via `#macro`; during
  normal play they fall through to the real functions. Don't fight it.
- **Prefer pure script-layer tests** (call functions directly; create no instances, step no
  rooms). Deterministic, fast, and immune to render/timing flakiness. Object *behavior*
  is covered by the autopilot instead (§5B).
- Gate the game against test mode: controller Create sets
  `global.testing = (environment_get_variable("GAME_RUN_TESTS") == "1")`, and the
  controller Step starts with `if (global.testing) exit;` so the game loop never fights
  the suites. Poll `gmtl_has_finished` → `game_end()` (an Alarm works).
- **Save-file trap:** tests that exercise persistence share the real save dir — a suite's
  `afterAll` can wipe the developer's actual save. Point tests at a separate save file, or
  accept and document that test runs reset the save.
- Restore every global you mutate (`beforeEach`/`afterEach` reset hooks) — suites run in
  one process, in order.

## 5B. Headless playtesting B: autopilot smoke runs

Tests prove functions; the **autopilot** proves the game actually plays. It's ~20 lines
in the controller object (full annotated version: `profiles/gamemaker/snippets/autopilot.gml`):

1. **Boot flag** in Create: `autopilot = (environment_get_variable("GAME_AUTOPILOT") == "1");`
   then auto-start past menus: `if (autopilot) start_run();`
2. **Input substitution at decision points** — wherever the player would press, branch on
   the flag with a deterministic "good" choice: `_lock = autopilot ? (meter >= 0.93) : _press;`
   Never simulate OS-level input; stay in-process.
3. **Mid-run evidence**, once past a progress threshold:
   `screen_save("debug_screenshot.png")` + a `show_debug_message("AUTOPILOT: ...")` marker.
4. **Deterministic exit**: on the results state, linger ~90 frames (so the screen renders),
   log final metrics (`"AUTOPILOT: dist=... views=..."`), then `game_end()`.
5. **Never hang on modal states**: any state waiting for a keypress (win banner, dialogs)
   must auto-advance under autopilot, or headless runs deadlock until the watchdog kills them.

The run's evidence = log lines + the screenshot in the save dir. Human-readable, diffable,
and citable in reviews ("autopilot reached 2281m, screenshot attached").

---

## 6. Working with rooms

A room is one `.yy` (e.g. `rooms/Room1/Room1.yy`) — `"$GMRoom":"v1"`. What an agent
actually touches:

- **`roomSettings`**: `Width`/`Height` in pixels, `persistent`.
- **`layers[]`** — ordered; each has a `depth` (higher = further back). Typical minimal
  setup: one `GMRInstanceLayer` ("Instances", depth 0) + one `GMRBackgroundLayer`
  ("Background", depth 100, `colour` as a packed ARGB integer). Remember the §4 depth trap.
- **Placing an instance by hand needs BOTH entries**:
  1. In the instance layer's `instances[]`: a `{"$GMRInstance":"v4", ...}` block with a
     unique `inst_XXXXXXXX` name (8 hex chars), `objectId` `{name, path}` pointing at the
     object's `.yy`, and `x`/`y`.
  2. In the room's top-level `instanceCreationOrder[]`:
     `{"name":"inst_XXXXXXXX","path":"rooms/<Room>/<Room>.yy",},`
- **`views[]`**: always 8 entries; enable with `viewSettings.enableViews: true` and set
  view 0 `visible: true` with `wview/hview` (camera size) and `wport/hport` (window size).
- **Runtime camera control beats room-file camera config**: keep the room's view static and
  drive `view_camera[0]` from the controller
  (`camera_set_view_pos(view_camera[0], x, y)`) — simpler to reason about and test.
- New room = folder + `.yy` + `.yyp` `resources` entry + `.yyp` `RoomOrderNodes` entry.
- The minimal-controller pattern: one room, one `obj_game` instance placed in it; obj_game
  spawns everything else from code. Rooms stay nearly empty and merge-safe.

---

## 7. Sprites & the art pipeline

**Sprite `.yy` anatomy** (clone an existing sprite and re-GUID rather than authoring fresh):

- `frames[]` — one `GMSpriteFrame` per frame, `name` = a fresh v4 GUID.
- `layers[]` — usually one `GMImageLayer`, its `name` also a GUID.
- **TWO identical PNGs per frame**: `sprites/<n>/<frameGUID>.png` AND
  `sprites/<n>/layers/<frameGUID>/<layerGUID>.png`. Missing the layers copy = broken sprite.
- An embedded `sequence` (GMSequence): `length` = frame count, one keyframe per frame in
  the frames track. `origin` (4 = middle-center), `bbox*` + `collisionKind` for collision.
- `width`/`height` must match the actual PNGs.

**Programmer-art-first workflow (proven):** build all gameplay with a 1×1 white `spr_pixel`
drawn scaled/tinted in Draw events (`draw_sprite_ext`). Collision masks and logic bind to
this proxy. When real art arrives, import real sprites and swap only the Draw events —
collision and logic stay untouched, so art integration can't break gameplay.

**External AI art lessons (image-model output is never game-ready):**

- Models return contact sheets with **painted-on checkerboard "transparency"** — it's
  opaque pixels, not alpha. Recovery: flood-fill de-checker from the corners + threshold,
  then slice into individual PNGs and resize to target canvas sizes (scriptable in Python/PIL).
- Ask the model for one contact sheet on a **solid unusual color** (e.g. magenta) instead
  of "transparent background" — keying out a solid is far more reliable.
- Expect a slicing/cleanup script to be part of the pipeline, not an exception.

---

## 8. Multi-agent parallel development

Proven pattern for N agents writing one GameMaker project simultaneously:

1. **Freeze interfaces first**: one shared contract script (enums, macros, function
   signatures) written by the coordinator before anyone codes. Agents code against the
   contract, never against each other's implementations.
2. **Disjoint file ownership**: every `.gml` belongs to exactly one agent. The coordinator
   pre-scaffolds all assets (folders, `.yy`, empty `.gml`, `.yyp` registration) so parallel
   agents never touch `.yyp` or `.yy` at all — they only fill `.gml` bodies.
3. **The seams are where the bugs live.** Adversarial review of the integrated result found
   7 real defects in the pilot — all at agent boundaries (objects ignoring the pause state,
   UI deviating from approved wireframes), none inside any single agent's file. Budget
   review time on cross-agent interactions: pause/state gating, shared globals, draw order,
   spec/wireframe fidelity.
4. Physics/economy/spawner/UI/tests is a natural 5-way split; tests-agent writes suites
   against the frozen contract while gameplay agents implement it.

---

## 9. Documentation access

- GML manual: https://manual.gamemaker.io/lts/en/ — **may be unreachable from studio
  networks** (verified: timeouts on IPv4+IPv6). Fallback order: (1) web-search for mirrored
  manual pages, (2) grep vendored libraries and a known-good prior project for working
  usage, (3) training knowledge with a `// TODO: verify against GML manual` comment.
  GML LTS is API-stable, so training knowledge is generally reliable for core functions.
- GMTL API: the vendored source itself + its GitHub wiki.

---

## 10. Quick-reference checklist (before claiming any GameMaker task done)

- [ ] IDE closed during structural changes (process check)
- [ ] New assets registered in `.yyp` `resources` alphabetically (+ `RoomOrderNodes` for rooms)
- [ ] Every event `.gml` has a matching `eventList` entry (types 0/2/3/8)
- [ ] No `score`/`lives`/`health` variables; no built-in function names as variables
- [ ] Custom draw depths < 100
- [ ] Sprites have both PNG copies + GMSequence keyframes; dimensions match
- [ ] Compile clean in the Igor log; tests pass (`run-tests.ps1` exit 0)
- [ ] Autopilot run produces log markers + screenshot (for gameplay changes)
- [ ] `.yy`/`.yyp` edits preserved trailing-comma style; no serializer round-trips
- [ ] Evidence captured: log path, test summary line, screenshot — not just "it works"

# GameMaker Engine Profile

Playsaurus engine profile for running the Agentic OS on **GameMaker (LTS)** projects.
Harvested from a real shipped pilot (the "Yeet-stone" prototype, July 2026): every rule and
script here survived a full governed cycle — 6 parallel subagents, 26 GMTL tests, adversarial
review, and an autopilot smoke run — before landing in this profile.

An engine profile fills the four slots the OS needs to let agents **verify their own work**:

| # | Slot | Provided by |
|---|---|---|
| 1 | Headless build/run | [`tools/run-game.ps1`](tools/run-game.ps1) (Igor CLI, captured log) |
| 2 | Headless tests | [`tools/run-tests.ps1`](tools/run-tests.ps1) (GMTL at boot, exit 0/1, runtime-error watchdog) |
| 3 | Automated smoke run | [`snippets/autopilot.gml`](snippets/autopilot.gml) (self-playing run + screenshot + metric log) |
| 4 | File-format safety rules | [`skills/gamemaker-gml/SKILL.md`](skills/gamemaker-gml/SKILL.md) |

## Installing into a GameMaker project

1. Deploy the Agentic OS normally (`installers/deploy_brain.ps1 -Target <project>`).
2. Copy `skills/gamemaker-gml/SKILL.md` → `<project>/.agents/skills/gamemaker-gml/SKILL.md`,
   and create the metadata stub dir `<project>/.agent/skills/gamemaker-gml/`.
   Replace the `<PROJECT>` placeholders (or let `/app-init` do it — point it at this file).
3. Copy `tools/*.ps1` → `<project>/tools/`. Override `-Runtime` if not on the LTS default path.
4. Vendor **GMTL** (DAndrewBox/GM-Testing-Library) into `scripts/GMTL_*`, then set its
   run-at-start macro to the env-var switch:
   `#macro gmtl_run_at_start (environment_get_variable("GAME_RUN_TESTS") == "1")`
   Keep all suites in one script (e.g. `scr_game_tests`) so ownership stays single-writer.
5. Wire the autopilot pattern from `snippets/autopilot.gml` into the game's controller object.
6. Prove the loop before writing gameplay: `run-tests.ps1` exits 0 on an empty suite and
   `run-game.ps1 -Autopilot` produces a log + screenshot. **A project is not agent-ready until
   both work.**

## Doc-lookup registry rows

Rows for `.agents/skills/doc-lookup/SKILL.md` in downstream projects:

| Technology | Official Doc URL | Notes |
|---|---|---|
| GameMaker GML | https://manual.gamemaker.io/lts/en/ | Functions, built-in variables, events |
| GMTL (test lib) | https://github.com/DAndrewBox/GM-Testing-Library | Vendored in `scripts/GMTL_*`; wiki has API |

> Verified 2026 (studio network): `gamemaker.io` domains can be unreachable (timeouts, IPv4+IPv6).
> Fallback order: (1) WebSearch for mirrored/cached manual pages, (2) grep the vendored GMTL
> source and a known-good prior project for usage patterns, (3) training knowledge with a
> `// TODO: verify against GML manual` caveat. GML LTS is API-stable, so (3) is usually safe
> for core functions.

## Known limits / backlog

- Scripts are Windows-only (Igor paths); no macOS/Linux variant yet.
- `installers/deploy_brain.ps1` does not deploy profiles automatically — install is manual
  (steps above). Candidate upstream extension: a `-Profile gamemaker` flag.
- Runtime version is pinned by parameter default; bump `-Runtime` when the LTS runtime updates.
- Unity will get a sibling profile (`profiles/unity/`) following the same four slots.

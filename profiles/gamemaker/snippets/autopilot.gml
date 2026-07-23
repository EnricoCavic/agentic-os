// AUTOPILOT PATTERN — engine-profile slot 3 (automated smoke run).
// Not a compilable script: adapt each block into the game's controller object.
// Harvested from a shipped pilot; the five moves below are what run-game.ps1 -Autopilot
// relies on to produce evidence (log lines + screenshot) without a human at the keyboard.

// ── 1. Boot flags (controller Create event) ─────────────────────────────────
// Both switches come from the environment so builds stay identical; only the
// launch context differs (see tools/run-game.ps1 / run-tests.ps1).
global.testing = (environment_get_variable("GAME_RUN_TESTS") == "1");
autopilot      = (environment_get_variable("GAME_AUTOPILOT") == "1");
// ...at the end of Create, skip menus so the run starts unattended:
if (autopilot) start_run();

// ── 2. Test mode freezes gameplay (controller Step event, first line) ───────
// GMTL suites drive everything themselves; the state machine must not fight them.
if (global.testing) exit;

// ── 3. Input substitution at decision points ────────────────────────────────
// Wherever the player would press/click, branch on the flag instead of reading
// input — pick a deterministic "good" value so runs are comparable across builds.
// Example (launch meter): lock near the top instead of reading the key.
_lock = autopilot ? (meter_power >= 0.93) : _press;

// ── 4. Mid-run evidence (once per run, past a progress threshold) ───────────
if (autopilot && !autopilot_shot_done && run_distance_m > 20) {
    screen_save("debug_screenshot.png");            // lands in the sandbox working dir
    show_debug_message("AUTOPILOT: screenshot saved"); // greppable in Igor stdout
    autopilot_shot_done = true;
}

// ── 5. Deterministic exit + final metrics (results state) ───────────────────
// Log the numbers the reviewer/test phase will assert on, then self-terminate.
// Igor reports a nonzero exit for automated stops — that is EXPECTED, not a failure;
// the harness judges the run by the log content.
if (autopilot) {
    results_timer++;
    if (results_timer >= 90) {                      // linger ~1.5s so the screen renders
        show_debug_message("AUTOPILOT: dist=" + string(run_result.dist_m)
            + " views=" + string(run_result.views));
        game_end();
    }
}

// ── Rule: never hang on modal states ────────────────────────────────────────
// Any state that waits for a keypress (win banner, dialogs) must auto-advance
// under autopilot, or headless runs deadlock until the watchdog kills them.
if (autopilot) { state = GameState.RESULTS; break; }

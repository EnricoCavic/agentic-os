# Work Log: docs/architecture-ondemand-clarify

## Header

- Branch: `docs/architecture-ondemand-clarify`
- Classification: `quick-win`
- Classified by: `claude-opus-4-8`
- Frozen: `2026-06-08`
- Created Date: `2026-06-08`
- Owner: `claude-opus-4-8 (luvseldom)`
- Guardrails Mode: `Quick`
- Current Phase: `ship`
- Checkpoint SHA: `954c108`
- Recommended Skills: `none`
- Primary Domain Snapshot: `governance-docs`
- SSoT Sequence: `41`

---

## Session Info

- Agent: `claude-opus-4-8`
- Session: `2026-06-08 10:00 UTC`
- Platform: `claude-code`
- Files Read: `6`

---

## Task Description

Spawned-task follow-up to the downstream simulation (#2): `docs/architecture/` is referenced by `engineering_guardrails.md` but not scaffolded on deploy. Investigation shows this is **intentional capability-by-presence design** (created on demand by `/app-init`; every consumer guards existence — bootstrap.md:145 "if not exist, skip; zero extra reads"). Option 1 (scaffold the dir) was REJECTED: it would regress the bootstrap zero-read optimization. Resolution = minimal option 2: clarify the one guardrail line that lacks an inline existence qualifier, and add a guard test locking in the no-scaffold design.

---

## Phase Sequence

| Phase | Status | Entered | Notes |
|---|---|---|---|
| bootstrap | done | 2026-06-08 | quick-win; finding is mostly false-alarm |
| plan | done | 2026-06-08 | line 107 qualifier + no-scaffold guard test |
| implement | done | 2026-06-08 | line 107 qualifier + no-scaffold guard test |
| ship | done | 2026-06-08 | committed; PR; SSoT |

---

## Phase Summary

- **bootstrap**: Verified the actual governance paths. `docs/architecture/` is deliberately on-demand (`app-init.md:104` creates it; `bootstrap.md:145` "If docs/architecture/ does not exist, skip all Domain Doc steps. Zero extra reads"; `bootstrap.md:140` AC-28 reads L1 only "AND a Domain Doc L1 exists"; `govern-docs.md:41` offers /app-init if absent). Unlike `docs/adr/` + `docs/specs/` (fixed anchors scaffolded with `.gitkeep.md`), architecture is NOT a fixed anchor. Subagent-C's "dangling reference" was a false alarm (every consumer guards presence). Source repo's own `docs/architecture/*.md` are framework-internal domain docs, correctly not deployed.
- **plan**: Reject option 1 (scaffolding regresses the zero-read optimization). Do option 2 minimal: (a) `engineering_guardrails.md:107` add "(if present; created by `/app-init`)" so the precedence rule is self-consistent with capability-by-presence; (b) add `tests/ci/test_deploy_tiering.py` guard asserting a fresh deploy does NOT create `docs/architecture/`, tied to the bootstrap.md:145 contract, to prevent a future wrong-fix.

---

## Gate Evidence

- Gate: bootstrap | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T10:00:00Z
- Gate: plan | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T10:05:00Z
- Gate: implement | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T10:15:00Z
- Gate: ship | Verdict: PASS | Classification: quick-win | Timestamp: 2026-06-08T10:25:00Z

---

## External References

| Type | Path / URL | Notes |
|---|---|---|
| Issue | task_de0c83fc (spawned chip) | from v1.4.0 downstream sim |
| PR | — | — |

---

## Known Risk

- Editing engineering_guardrails.md (a constitution file) — change is a 4-word inline clarifier matching implemented behavior, no semantic rule change. Low risk.

---

## Conflict Resolution

none

---

## Skill Notes

none

---

## Drift Log

- Ship SSoT write applied directly via Edit (Ship History + Update Sequence 41→42 + Last Updated), not via `guard_context_write.py` — guard section-targeting doesn't cover combined append + header update. Logged per AGENTS.md guard-fallback discipline.

---

## Design Reference

none

---

## Observability

none

---

## Resume

none

---

## Evidence

- Capability-by-presence proof: `bootstrap.md:145` "If `docs/architecture/` does not exist, skip all Domain Doc steps below. Zero extra reads."; `app-init.md:104` "Create `docs/architecture/` if it does not exist."
- Deploy contrast: deploy.sh `mkdir -p docs/specs docs/adr` + ships `docs/{specs,adr}/.gitkeep.md`; NO architecture entry → architecture intentionally not a fixed anchor.
- `pytest -k "docs_architecture or referenced_tools"` → 2 passed (new no-scaffold guard + referenced-tools regression).
- `bash validate.sh` → pass=101 warn=7 fail=0 (guardrails edit did not break any encoding canary).

⚡ ACX

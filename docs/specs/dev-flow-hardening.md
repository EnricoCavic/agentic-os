---
status: draft
classification: architecture-change
primary_domain: governance-runtime
signal_tier: T1
secondary_domains:
  - ci-security
  - downstream-adaptability
  - developer-experience
created: 2026-06-29
owner: codex-session
---

# Development Flow Hardening

## Goal

Turn the verified development-flow audit findings into a small set of machine-checkable improvements that match Agentic OS product philosophy: downstream projects own their own state, gates must be honest rather than theatrical, no-Python and docs-only paths must state their reduced assurance, and broad governance changes must ship in reversible batches with evidence.

## Acceptance Criteria

- **AC-1 Downstream SSoT isolation**: Deploy never installs the source repository's live `.agentcortex/context/current_state.md` into downstream projects. The deploy path must use `.agentcortex/templates/current_state.md` and fail closed if that template is missing. Verification includes a temp downstream deploy proving the installed SSoT contains template placeholders and no source-repo project markers.
- **AC-2 Deploy dry-run honesty**: Dry-run output must disclose that `.agentcortex/context/current_state.md` will be created from the template, not merely list the template file. Verification asserts the dry-run preview and real deploy agree on this install artifact.
- **AC-3 Gate receipt enforcement truth**: `/ship` and validator behavior must not describe missing required phase receipts as blocking unless a machine check actually blocks. For the source repo and direct-file-access platforms, missing required receipts for architecture-change work must fail `/ship`; platform paths without direct file access must fail until the required receipt is pasted or mirrored. Any retained advisory path must say `advisory` or `reduced assurance`.
- **AC-4 Checkpoint SHA split**: The workflow must distinguish `Diff Base SHA` (immutable pre-implementation review base) from `Checkpoint SHA` (latest resumable/current HEAD anchor). Review diff selection uses `Diff Base SHA`; handoff/resume checks use `Checkpoint SHA`. Legacy Work Logs that lack `Diff Base SHA` may fall back to `Checkpoint SHA` with a one-time WARN, not silent reinterpretation.
- **AC-5 Evidence verifier honesty**: `verify_agent_evidence.py` must report three cases accurately: repo not opted into review mirrors = SKIP/WARN with reduced-assurance wording; opted-in mirror path present but no changed mirror = WARN unless strict mode is enabled; explicit path/worklog input that cannot be inspected = FAIL. It must not return success with text implying changed Work Logs were checked when no artifacts were inspected.
- **AC-6 Active Work Log state is actionable**: Validator findings for shipped-but-active logs, phase/header mismatch, incomplete resume blocks, and missing test-gate results must be tiered according to product impact. Current-branch gate invariants fail; historical hygiene remains WARN. Any issue documented as a gate invariant must be machine-enforced; remaining advisory findings must use honest WARN wording.
- **AC-7 CI/security claims match branch protection reality**: Repository docs and validation must not imply security jobs are required branch checks unless branch protection actually requires them. Local code must not mutate branch protection; implementation must either update claims to match the observed required checks or document the maintainer-owned setting required to make security a merge floor.
- **AC-8 Credential floor cannot fail open silently**: Source-repo CI paths that call `scan_credentials.py` must fail closed on scanner execution errors. Optional local/downstream hook paths may WARN on Python enrichment errors only when the native credential floor still ran; otherwise they must block or state reduced assurance explicitly. Verification covers non-zero scanner exit handling and the existing `pragma: allowlist secret` behavior.
- **AC-9 Dependency audit coverage is complete for repo-owned CI deps**: Security dependency scans must include `.github/requirements-ci.txt` or document why that file is out of scope. Verification injects a controlled vulnerable or detectable dependency fixture without committing real vulnerable dependencies.
- **AC-10 Default test command is safe**: The default or documented `pytest` command must not collect ignored/demo/root cache files that require unavailable secrets. Verification proves a clean local command exercises the intended test surface or that the documented command is narrowed and enforced.
- **AC-11 PowerShell flag parity is honest**: `validate.ps1 --no-python` and `validate.ps1 -NoPython` must behave consistently or docs/help must make the distinction impossible to misunderstand. Verification covers both spellings.
- **AC-12 Docs-only classifier is threat-aware**: CI skip logic must distinguish inert prose-only docs from operational governance/state files such as workflows, rules, validators, templates, and context artifacts. Verification shows operational governance docs cannot skip security-relevant jobs by being under a broad docs path.

## Non-goals

- Do not rewrite the whole validator stack or state machine in one pass.
- Do not make every existing WARN a FAIL; only promote findings with a clear machine-checkable invariant and low false-positive risk.
- Do not automate branch-protection mutation from local scripts; if required checks need changing, document the exact repository setting or CI contract separately.
- Do not retroactively repair every archived Work Log unless a current validator or ship gate consumes it.
- Do not change downstream projects' local state ownership model; source repo templates bootstrap downstream state, but source repo runtime state is never an install artifact.

## Constraints

- All implementation batches must preserve Write Isolation: only `/ship` updates `.agentcortex/context/current_state.md`.
- Subagents may analyze and propose, but the primary agent remains the sole Work Log writer and gate owner.
- The remediation must be reviewable as small, reversible changes; one spec may coordinate multiple batches, but each batch needs targeted evidence.
- No secrets or real credentials may be introduced in fixtures, logs, commands, or docs.
- Downstream compatibility matters: missing Python or missing optional GitHub features should degrade honestly, not silently claim full protection.

## File Relationship

**EXTENDS** `docs/specs/downstream-adaptability-optimization.md` by tightening the install boundary between source-repo state and downstream-owned state.

**EXTENDS** `docs/specs/ci-security-scanning.md` and `docs/specs/pre-commit-local-validation.md` by requiring CI/security and credential-floor claims to match actual enforcement.

**RELATED TO** `docs/specs/validator-strangler-policy.md`, `docs/specs/worklog-lock-auto-recovery.md`, and `docs/specs/frozen-spec-lifecycle.md`; this spec must not duplicate their machinery or change frozen spec lifecycle rules.

## Settled Document Alignment

| Settled source | Status | Constraint applied here |
|---|---:|---|
| `docs/adr/ADR-005-downstream-file-preservation-tiering.md` | accepted | Framework-authoritative files may force-update, but downstream-owned/custom state must not be silently overwritten. |
| `docs/adr/ADR-006-validator-python-core-strangler.md` + `docs/specs/validator-strangler-policy.md` | accepted / shipped | New validator checks default to Python tools behind both wrappers; native shell/PowerShell growth needs a no-Python protection rationale and baseline justification. |
| `docs/adr/ADR-007-downstream-capability-declaration-seam.md` | accepted | Downstream extension state is present-only, gitignored/private, never shipped by deploy, and never allowed to relax gates. |
| `docs/adr/ADR-008-portable-safety-floor.md` | accepted | Safety and credential controls must be portable; no-Python paths may be reduced assurance, but never silent equivalence. |
| `docs/adr/ADR-010-frozen-spec-lifecycle.md` + `docs/specs/frozen-spec-lifecycle.md` | accepted / shipped | Pre-ship spec/freeze phases do not write SSoT; `/ship` remains the sole SSoT indexer. |
| `docs/specs/ci-security-scanning.md` | shipped | Security jobs exist and should protect PRs, but claims about required merge checks must match live branch protection. |
| `docs/specs/pre-commit-local-validation.md` | shipped | Local hooks are opt-in; advisory guarded-write warnings remain advisory, but credential scanning must not fail open silently. |

## Enforcement Decisions

| Area | Decision | Why |
|---|---|---|
| Downstream SSoT | Deploy may create downstream `.agentcortex/context/current_state.md` only from `.agentcortex/templates/current_state.md`; missing template is a source packaging error and fails closed. | Source live state is not a product artifact; downstream owns its runtime SSoT. |
| Ship receipts | Required architecture-change receipts are hard gates when the Work Log is inspectable. | `NO EVIDENCE = NO COMPLETION`; otherwise receipts become self-attested theater. |
| Evidence mirrors | Missing optional mirrors are reduced assurance, not success. Explicit requested evidence that cannot be inspected fails. | Optional capability-by-presence is allowed; misleading success is not. |
| Branch protection | Do not mutate repository rules from local code. Claims and install docs must match the observed required-check list unless a maintainer changes it. | Branch protection is repository administration, not a deploy/runtime artifact. |
| Credential scanner errors | Source CI fails closed; optional hooks may WARN only after a native no-Python floor has run. | Secrets controls are safety floor work, but local hooks remain opt-in and downstream-variable. |
| Docs-only skip | Inert prose may skip heavy jobs; governance/runtime/security docs cannot skip security-relevant jobs solely because they live under `docs/` or `.agentcortex/context/`. | Operational docs encode product behavior and can change gates. |

## Active Work Log Severity Table

| Finding | Current branch / current phase | Historical or unrelated logs |
|---|---|---|
| Missing required gate receipt after a phase that requires it | FAIL | WARN |
| Ship PASS receipt while `Current Phase` is not `ship` | FAIL at `/ship` validation | WARN |
| Feature/architecture-change reaches handoff/ship with no `Test Gate Results` evidence | FAIL | WARN |
| `## Resume` missing required handoff subsections for current handoff/ship | FAIL | WARN |
| Shipped Work Log still active rather than archived | FAIL for current `/ship`; WARN for stale active history | WARN |
| Active Work Log count over hygiene threshold or stale advisory locks | WARN | WARN |

## Domain Decisions

- [DECISION] Source-repo live state is not a deployable product asset; downstream installs receive templates and then own their local SSoT.
- [DECISION] Gates are only gates when a validator or workflow check can fail closed; otherwise wording must say advisory or reduced assurance.
- [DECISION] The fix set is one architecture-change spec but multiple implementation batches, because review quality is part of the product.
- [DECISION] Security and credential checks fail closed in source CI, while optional downstream/local paths can degrade only with explicit reduced-assurance wording.
- [TRADEOFF] Some current WARNs may remain WARNs where historical data or downstream variance would make a hard fail noisy; the tradeoff is acceptable only with honest wording.
- [CONSTRAINT] No-Python paths, docs-only skips, and hook samples must never silently claim the same assurance as full CI/Python paths.
- [CONSTRAINT] Work Log ownership remains single-writer; subagent findings are evidence inputs, not independent gate receipts.

## Proposed Implementation Batches

1. **Downstream state boundary**: remove the live SSoT fallback in deploy, update dry-run preview, add deploy regression tests.
2. **Evidence and gate honesty**: harden or reword ship receipt audit, evidence verifier, active Work Log validator messages, and checkpoint fields.
3. **CI/security enforcement truth**: reconcile branch-protection claims, docs-only skip behavior, dependency audit coverage, and credential scanner fail-open paths.
4. **Developer command hygiene**: fix or document default pytest collection and PowerShell no-Python flag parity.

- **AC-13 Demonstration over green gates**: Changes that touch user-facing surfaces (deploy output, validator output, README) require an anchored demonstration — a real run whose output is captured and CI-enforced — not just green correctness gates. For the deploy surface: a normalized manifest snapshot (`tests/ci/fixtures/deploy_manifest_golden.txt`) is committed and asserted by `test_deploy_manifest_snapshot` in `tests/ci/test_deploy_tiering.py`; CI re-runs the real `deploy.sh` so a hand-faked golden diverges and stays red. The paved one-command recipe is `.agentcortex/tools/demo_deploy.sh`. **Honest-ceiling clause**: surfaces that CI actually executes (deploy) get anchored enforcement; surfaces that nothing executes (README render, holistic "reads right") remain honestly ADVISORY — no screenshot/golden harness is built (there is no in-repo CI consumer for rendered README output).

## Verification Plan

- Run source validator on Python-present and no-Python modes: `validate.ps1`, `validate.ps1 -NoPython`, and `validate.ps1 --no-python`.
- Run targeted pytest files for deploy tiering, credential scanning, evidence verification, workflow validation, and CI classifier behavior.
- Run a temp downstream deploy and inspect the installed `.agentcortex/context/current_state.md`.
- Run dry-run deploy and compare the previewed install artifacts against real deploy outputs.
- Run branch-protection inspection via `gh api` when GitHub auth is available, and document the exact required-check result as evidence.

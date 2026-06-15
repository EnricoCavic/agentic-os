#!/usr/bin/env python3
"""Schema gate-safety validator for downstream-capabilities.yaml (ADR-007 AC-D6).

Makes gate-relaxation UNREPRESENTABLE: a present capabilities file is REJECTED
(exit 1, naming the offending field) - never silently clamped - if it registers a
non-`custom-*` skill, raises a skill above the `on-match` load_policy ceiling, or
declares anything that could relax/escalate a gate (gate / ship-edge / block_if_missed
/ trigger_priority / concurrent-writer / blocking tracker).

  exit 0 = gate-safe (or absent / empty -> inert)
  exit 1 = NOT gate-safe (reason on stderr)
  exit 2 = malformed / unreadable

Parsed via the repo's `_yaml_loader` (PyYAML when installed, else a dependency-free
subset). Cap-evasion via YAML anchors/aliases/merge-keys is caught regardless of parser:
the recursive denylist + the top-level/skill-key ALLOWLIST reject the *resolved* keys,
so the guarantee is structural, not a property of the parser. When Python is absent the
validator is SKIPped by validate.* (run_python_check); the file is inert at runtime
until an agent reads it, so this source/CI-side check is the machine guarantee.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import _yaml_loader
except Exception as exc:  # pragma: no cover - deployed alongside in runtime_tools
    sys.stderr.write("ERROR: _yaml_loader unavailable (%s)\n" % exc)
    sys.exit(2)

ALLOWED_LOAD_POLICY = {"on-match"}
ALLOWED_SUBAGENT_POLICY = {"read-only", "governed"}
# keys that could relax / escalate a gate anywhere in the doc -> hard reject (fail-closed)
FORBIDDEN_KEYS = {"gate", "gates", "ship_edge", "ship_edges", "block_if_missed",
                  "trigger_priority", "worklog_writers", "blocking", "hard"}


def _forbidden(obj, where="root"):
    if isinstance(obj, dict):
        for key, val in obj.items():
            if str(key).strip().lower() in FORBIDDEN_KEYS:
                return "%s.%s" % (where, key)
            hit = _forbidden(val, "%s.%s" % (where, key))
            if hit:
                return hit
    elif isinstance(obj, list):
        for i, val in enumerate(obj):
            hit = _forbidden(val, "%s[%d]" % (where, i))
            if hit:
                return hit
    return None


def validate(data):
    """Return None if gate-safe, else a 1-line reason naming the offending field."""
    if data is None or data == {}:
        return None  # empty / absent = inert = safe (present-only)
    if not isinstance(data, dict):
        return "top-level must be a mapping"
    hit = _forbidden(data)
    if hit:
        return "forbidden gate-relaxing key: %s" % hit
    # ALLOWLIST (not just a denylist): an unknown top-level key cannot be smuggled in
    # as a future escalation surface -> gate-relaxation is structurally unrepresentable.
    for key in data:
        if str(key) not in {"version", "skills", "subagent_policy", "trackers"}:
            return ("unknown top-level key %r - only version/skills/subagent_policy/trackers "
                    "are allowed (gate-relaxation is unrepresentable)" % key)
    for i, sk in enumerate(data.get("skills") or []):
        if not isinstance(sk, dict):
            return "skills[%d] must be a mapping" % i
        sid = str(sk.get("id", ""))
        if not sid.startswith("custom-"):
            return "skills[%d].id %r is not custom-* (downstream skills MUST be custom-*)" % (i, sid)
        lp = sk.get("load_policy", "on-match")
        if lp not in ALLOWED_LOAD_POLICY:
            return "skills[%d].load_policy %r must be on-match (the downstream capability ceiling)" % (i, lp)
        ps = sk.get("phase_scope")
        if ps is not None and not isinstance(ps, list):
            return "skills[%d].phase_scope must be a list" % i
        for sk_key in sk:
            if str(sk_key) not in {"id", "load_policy", "phase_scope", "detect_by", "cost_risk", "description"}:
                return "skills[%d] unknown key %r (allowlist: id/load_policy/phase_scope/detect_by/cost_risk/description)" % (i, sk_key)
    sp = data.get("subagent_policy", "read-only")
    if sp not in ALLOWED_SUBAGENT_POLICY:
        return "subagent_policy %r invalid (allowed: read-only | governed)" % sp
    for i, tr in enumerate(data.get("trackers") or []):
        if not isinstance(tr, dict):
            return "trackers[%d] must be a mapping" % i
    return None


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: validate_downstream_capabilities.py <file>\n")
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        return 0  # absent = inert = safe (present-only)
    try:
        data = _yaml_loader.load_data(path)
    except Exception as exc:
        sys.stderr.write("MALFORMED: cannot parse %s (%s)\n" % (path, exc))
        return 2
    reason = validate(data)
    if reason is None:
        sys.stdout.write("OK: downstream-capabilities.yaml is gate-safe\n")
        return 0
    sys.stderr.write("FAIL: downstream-capabilities.yaml is NOT gate-safe - %s\n" % reason)
    return 1


if __name__ == "__main__":
    sys.exit(main())

---
phase: 01
slug: policy-foundation-and-threat-boundaries
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-29
verified: 2026-04-29
---

# Phase 01 — Security

Per-phase security contract for policy foundation, egress enforcement, audit baseline, and `verify-policy`.

## Trust boundaries

| Boundary | Description | Data crossing |
|----------|-------------|---------------|
| Config file → policy loader | Untrusted JSON policy input affects enforcement | Policy JSON |
| CLI / env → profile resolver | Runtime profile selection changes posture | Profile name, optional policy path |
| Runtime operation → egress guard | Outbound actions need authorization | URLs, operation labels, payload classification |
| Embeddings → network | Provider calls may exfiltrate embedding inputs | HTTP to cloud APIs |
| Policy / guard decisions → audit sink | Security outcomes persisted locally | JSONL metadata |
| Operator → `verify-policy` | Automation relies on exit code and output | Human/script trust in PASS/FAIL |

## Threat register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-01-01 | T | `policy_loader.py` | mitigate | `HardenedPolicy.model_validate`; `PolicyLoadError` on invalid/missing file; audit on failure | **closed** — `tests/test_policy_schema.py`, `load_policy` |
| T-01-02 | E | Profile selection (`resolve_policy_for_profile`, CLI) | mitigate | `PolicyMode.HARDENED_LOCAL`; egress `default_action` deny; `--security-profile` sets env | **closed** — `policy_schema.py`, `cli._apply_cli_security_profile`, tests |
| T-01-03 | R | Policy initialization failures | mitigate | `emit_audit_record` on load failures (`policy_load_failure`) | **closed** — `policy_loader.py`, `tests/test_policy_audit.py` |
| T-01-04 | I | `embeddings.py` outbound | mitigate | `_enforce_embedding_egress` / `check_egress` before cloud branches | **closed** — `tests/test_embeddings.py` (`TestHardenedLocalEgressEnforcement`) |
| T-01-05 | E | `egress_guard.py` decision path | mitigate | Deny on unknown operation/host under hardened; explicit `EgressDecision` | **closed** — `tests/test_egress_guard.py` |
| T-01-06 | R | Deny decisions observable | mitigate | `emit_audit_record` from guard; reason codes on `EgressDecision` | **closed** — `egress_guard.py`, audit tests |
| T-01-07 | R | Audit event storage | mitigate | JSONL with `REQUIRED_FIELDS`; structured records | **closed** — `audit.py`, `tests/test_policy_audit.py` |
| T-01-08 | I | Audit payload sensitivity | mitigate | `_scrub_metadata` strips bodies; tests for audit contract | **closed** — `audit.py`, `tests/test_policy_audit.py` |
| T-01-09 | T | `verify-policy` output | mitigate | Exit codes 0/1/2; JSON/human; tied to resolved policy + egress probe | **closed** — `cli._handle_verify_policy`, `tests/test_policy_verify.py` |

## Accepted risks log

No accepted risks.

## Security audit trail

| Audit date | Threats total | Closed | Open | Run by |
|------------|---------------|--------|------|--------|
| 2026-04-29 | 9 | 9 | 0 | `/gsd-secure-phase 01` (inline verification vs implementation) |

## Evidence commands

```bash
uv run pytest tests/test_policy_schema.py tests/test_egress_guard.py tests/test_embeddings.py \
  tests/test_policy_audit.py tests/test_policy_verify.py tests/test_main.py tests/test_tools.py -q
```

## Sign-off

- [x] All threats have disposition **mitigate** with evidence
- [x] Accepted risks: none
- [x] `threats_open: 0`

**Approval:** verified 2026-04-29

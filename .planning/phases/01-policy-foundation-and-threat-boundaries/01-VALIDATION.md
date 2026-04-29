---
phase: 01
phase_slug: policy-foundation-and-threat-boundaries
created: 2026-04-29
status: active
---

# Validation Strategy - Phase 01

## Validation Architecture

- Objective: validate local-only policy enforcement for REQ-01, REQ-02, REQ-06, and REQ-07.
- Primary gate: deny-by-default behavior in hardened-local mode.
- Secondary gate: offline-capable core workflows with no cloud dependency.
- Evidence model: automated test output + deterministic CLI verification status.

## Dimension Coverage

1. **Policy correctness**: schema strictness and fail-closed policy loading.
2. **Egress enforcement**: centralized deny-before-network for protected payload classes.
3. **Offline operation**: build/update/query/review-context workflows run with hardened-local defaults and no cloud credentials.
4. **Audit baseline**: local structured events emitted for allow/deny/load/verify actions.
5. **Operator verification**: CLI policy verification returns machine-readable pass/fail and non-zero on non-compliance.

## Commands

- `uv run pytest tests/test_policy_schema.py -q`
- `uv run pytest tests/test_egress_guard.py tests/test_embeddings.py -q`
- `uv run pytest tests/test_main.py tests/test_tools.py -q`
- `uv run pytest tests/test_policy_audit.py tests/test_policy_verify.py -q`

## Exit Gates

- All commands pass in hardened-local profile.
- At least one test asserts cloud egress denial for protected classes.
- At least one test asserts offline success for build/update/query/review-context flows.
- Verification command contract is stable and automation-friendly.

---
phase: 01
phase_slug: policy-foundation-and-threat-boundaries
created: 2026-04-29
status: complete
nyquist_compliant: true
wave_0_complete: true
last_validated: 2026-04-29
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

## Validation audit (2026-04-29)

Nyquist pass over Phase 01 bundle; gaps closed:

| Metric | Count |
|--------|-------|
| Gaps found | 1 |
| Resolved | 1 |
| Escalated | 0 |

**Gap resolved:** `_apply_tool_filter` and `TestApplyToolFilter` referenced removed FastMCP internals (`_tool_manager`). Updated `main.py` to use `await mcp.list_tools(run_middleware=False)` + `mcp.local_provider.remove_tool(name)`, and rewrote tests to avoid nested `asyncio.run` while restoring removed tools via `add_tool`.

**Commands re-verified (green):**

```bash
uv run pytest tests/test_policy_schema.py tests/test_egress_guard.py tests/test_embeddings.py \
  tests/test_main.py tests/test_tools.py tests/test_policy_audit.py tests/test_policy_verify.py -q
```

Result: **202 passed** (same bundle as listed in Commands section above).

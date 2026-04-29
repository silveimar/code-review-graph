---
phase: 01-policy-foundation-and-threat-boundaries
plan: 02
subsystem: security
tags: [egress, embeddings, policy, hardened-local, pytest]

requires:
  - phase: 01-policy-foundation-and-threat-boundaries
    provides: policy schema and fail-closed loader from plan 01-01
provides:
  - Centralized egress guard API with machine-readable deny reasons
  - Embedding provider paths blocked before HTTP when hardened-local denies cloud egress
  - CLI `--security-profile` wiring to CRG_SECURITY_PROFILE for operators
  - Automated offline core-workflow tests under hardened-local (build + review context)
affects:
  - phase: 01-policy-foundation-and-threat-boundaries
  - embeddings integrations and future outbound adapters

tech-stack:
  added: []
  patterns:
    - "check_egress(policy, operation, destination, classification) fail-closed decisions"
    - "PermissionError carries EgressReasonCode for audit-oriented callers"

key-files:
  created:
    - code_review_graph/security/egress_guard.py
    - tests/test_egress_guard.py
  modified:
    - code_review_graph/embeddings.py
    - code_review_graph/cli.py
    - code_review_graph/security/__init__.py
    - tests/test_embeddings.py
    - tests/test_main.py
    - tests/test_tools.py

key-decisions:
  - "Default CRG_SECURITY_PROFILE remains standard when unset so existing cloud embedding tests and CI behavior stay unchanged; hardened-local is opt-in via env or --security-profile."
  - "Google/MiniMax egress checks use canonical HTTPS URLs aligned with provider endpoints for deterministic policy tests."

requirements-completed: [REQ-01, REQ-02, REQ-06]

duration: 35 min
completed: 2026-04-29
---

# Phase 1 Plan 2: Centralized Egress Guard Summary

**Fail-closed egress guard with embedding enforcement, CLI profile export, and hardened-local offline workflow regression tests.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-04-29 (executor session)
- **Completed:** 2026-04-29
- **Tasks:** 3
- **Files touched:** 8

## Accomplishments

- Implemented `check_egress()` with explicit allow/deny outcomes and stable `EgressReasonCode` values for downstream audit use (REQ-06 baseline surface).
- Wired OpenAI, MiniMax, and Google embedding paths to enforce policy before instantiating providers; hardened-local denies public cloud hosts while allowing loopback gateways.
- Added `--security-profile hardened_local|standard` on the root CLI parser and tests proving core `build_or_update_graph` / `get_review_context` paths succeed without cloud credentials when hardened-local is active (REQ-02).

## Task Commits

1. **Task 1: Build centralized egress guard module** — `9fe5990` (feat)
2. **Task 2: Enforce guard in embeddings outbound paths** — `36bd0e0` (feat)
3. **Task 3: Offline-capable core workflows under hardened-local** — `2e3cd16` (feat)

**Plan metadata:** Included in `docs(01-02): complete egress guard plan execution` commit (SUMMARY + STATE + ROADMAP).

## Files Created/Modified

- `code_review_graph/security/egress_guard.py` — Decision API, URL hostname parsing, hardened vs standard branching.
- `tests/test_egress_guard.py` — Matrix tests for deny cloud, allow local, unknown operation, invalid destination, policy override.
- `code_review_graph/embeddings.py` — `_active_security_policy`, `_enforce_embedding_egress`, `get_provider(..., policy=...)`.
- `code_review_graph/cli.py` — `_apply_cli_security_profile`, global `--security-profile`.
- `tests/test_embeddings.py` — Hardened denial/allow cases for cloud vs loopback OpenAI and MiniMax.
- `tests/test_main.py` — `TestCliSecurityProfile` for env wiring.
- `tests/test_tools.py` — `TestHardenedLocalOfflineCoreWorkflows` for build + review context under hardened-local.

## Decisions Made

- Followed plan research: hostname parsing via `urlparse` for nip.io-style bypass resistance; reuse policy `allowed_local_destinations` list.

## Deviations from Plan

### Auto-fixed Issues

None — plan executed as written.

### Verification notes

- Plan listed `uv run ruff check ...`; the project `.venv` in this environment did not expose a working `ruff` executable (`uv run ruff` / `python -m ruff` unavailable). Lint was not re-run via CI here; recommend `uv sync` / dev extras locally before merge.

### Scope / pre-existing tests

- Full `tests/test_main.py` currently reports unrelated failures (`TestServeMainTransport` expectation vs `show_banner`, `TestApplyToolFilter` FastMCP `_tool_manager` attribute). These were not introduced by this plan; verification focused on plan-listed suites and new tests.

## Issues Encountered

None blocking completion.

## REQ-06 scope note

Structured denial reasons (`EgressDecision`, `PermissionError` text) satisfy the plan’s “audit baseline” / REQ-06 wiring for this wave; durable JSONL audit emission remains for plan 01-03 per roadmap.

## User Setup Required

None — no new secrets. Operators may set `CRG_SECURITY_PROFILE=hardened_local` or pass `--security-profile hardened_local`.

## Next Phase Readiness

Ready for **01-03** (verification report + durable audit events). Egress enforcement is centralized for embeddings; additional outbound surfaces should call `check_egress` the same way.

## Self-Check: PASSED

- `code_review_graph/security/egress_guard.py` exists.
- `tests/test_egress_guard.py` exists.
- Commits `9fe5990`, `36bd0e0`, `2e3cd16` present on branch.
- `uv run pytest tests/test_egress_guard.py tests/test_embeddings.py -q` passed; targeted new tests in `tests/test_main.py` / `tests/test_tools.py` passed.

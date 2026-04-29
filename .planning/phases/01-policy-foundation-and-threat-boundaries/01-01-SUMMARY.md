---
phase: 01-policy-foundation-and-threat-boundaries
plan: 01
subsystem: security
tags: [policy, hardened-local, fail-closed, pydantic, offline]
requires: []
provides:
  - Hardened local policy schema with deny-by-default egress defaults
  - Fail-closed policy loader with deterministic profile resolution
  - Regression tests for strict schema and loader contract behavior
affects: [egress-enforcement, audit-layer, verification]
tech-stack:
  added: []
  patterns: [strict schema validation, fail-closed loading, profile-based defaults]
key-files:
  created:
    - code_review_graph/security/policy_schema.py
    - code_review_graph/security/policy_loader.py
    - code_review_graph/security/__init__.py
    - tests/test_policy_schema.py
  modified:
    - code_review_graph/security/policy_schema.py
    - code_review_graph/security/__init__.py
key-decisions:
  - "Use typed Pydantic policy models with explicit protected data classes for hardened-local defaults."
  - "Treat missing/invalid policy sources as hard errors via PolicyLoadError (never permissive fallback)."
patterns-established:
  - "Security policy defaults to deny outbound egress in hardened_local mode."
  - "Runtime profile resolution is deterministic and validated against policy mode."
requirements-completed: [REQ-01, REQ-02]
duration: 3 min
completed: 2026-04-29
---

# Phase 1 Plan 1: Hardened Policy Contract Summary

**Shipped a strict hardened-local policy schema and fail-closed loader contract that blocks permissive policy fallback and keeps offline defaults deterministic.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-29T15:01:55Z
- **Completed:** 2026-04-29T15:05:32Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Added strict policy schema models for mode, egress, protected data classes, and audit defaults.
- Implemented fail-closed policy loading with explicit `PolicyLoadError` paths for missing/invalid configs.
- Added hardened-local and standard profile resolution with deterministic defaults.
- Added regression tests covering unknown keys, invalid values, missing source failure, and valid config loading.

## Task Commits

Each task was committed atomically:

1. **Task 1: Define hardened-local policy schema** - `1acc72c` (test), `06c6558` (feat)
2. **Task 2: Implement fail-closed policy loader contract** - `4f97f7e` (test), `7d1101c` (feat)
3. **Verification fix:** `8deeb3d` (fix)

## Files Created/Modified
- `code_review_graph/security/policy_schema.py` - strict schema and hardened-local defaults.
- `code_review_graph/security/policy_loader.py` - fail-closed loader and profile resolver.
- `code_review_graph/security/__init__.py` - stable security API exports.
- `tests/test_policy_schema.py` - schema and loader contract tests.

## Decisions Made
- Used enum-backed policy fields with explicit protected payload classes (`source_snippet`, `symbol_context`, `full_file_content`, `embedding_input`) to enforce a reusable contract.
- Kept hardened-local defaults cloud-deny and local-destination allowlist based for offline-safe behavior.
- Enforced mode/profile consistency when loading explicit policy files to avoid ambiguous runtime posture.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Relaxed enum parsing strictness for JSON policy input**
- **Found during:** Task 2 (loader verification)
- **Issue:** Initial strict model settings rejected valid string enum values from JSON policy files.
- **Fix:** Kept `extra="forbid"` and strict scalar fields while allowing enum string parsing.
- **Files modified:** `code_review_graph/security/policy_schema.py`
- **Verification:** `uv run pytest tests/test_policy_schema.py -q`
- **Committed in:** `7d1101c`

**2. [Rule 3 - Blocking] Switched lint verification to `uvx ruff`**
- **Found during:** Plan verification
- **Issue:** `uv run ruff` was unavailable in the active interpreter toolchain.
- **Fix:** Used `uvx ruff` for deterministic lint execution without changing project dependencies.
- **Files modified:** none
- **Verification:** `uvx ruff check code_review_graph/security tests/test_policy_schema.py`
- **Committed in:** n/a (verification-path adjustment only)

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both fixes were required to satisfy fail-closed behavior and complete required verification gates without scope creep.

## Issues Encountered
- `ruff` was not directly invokable through `uv run` in this shell environment; verification proceeded successfully with `uvx ruff`.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Policy schema and loader contracts are now available for downstream enforcement/audit integration.
- Ready for `01-02-PLAN.md`.

## Self-Check: PASSED

---
*Phase: 01-policy-foundation-and-threat-boundaries*
*Completed: 2026-04-29*

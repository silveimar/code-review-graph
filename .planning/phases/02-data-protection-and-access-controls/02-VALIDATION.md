---
phase: 02
phase_slug: data-protection-and-access-controls
created: 2026-04-29
status: pending
---

# Validation Strategy — Phase 02 (Nyquist / Operator Gates)

## Validation Architecture

- **Objective:** Validate data protection and access controls for **REQ-03**, **REQ-04**, and **REQ-06** under `hardened_local` and standard contrast.
- **Primary gate:** No plaintext persistent sensitive artifacts when policy requires application-layer encryption and key material is absent (fail-closed, D-03).
- **Secondary gate:** Data directory permissions match documented hardened expectations on POSIX.
- **Tertiary gate:** Local audit JSONL includes Phase 2 event types for denials and permission outcomes.
- **Evidence model:** automated pytest + subprocess CLI checks + optional manual inspection of temp audit files.

## Dimension Coverage

1. **Encryption policy (REQ-03):** Schema fields, key resolution, refuse vs allow matrix.
2. **Graph and file artifacts (D-02):** `graph.db`, `policy_audit.jsonl`, `memory/`, `wiki/` paths when encryption enabled.
3. **Filesystem permissions (REQ-04):** `0o700` / `0o600` (or documented no-op) and verify-policy output.
4. **Audit expansion (REQ-06):** New `event_type` / `operation` values with scrubbed metadata.
5. **Regression:** Standard profile and offline workflows remain viable (Phase 1 contract preserved).

## Commands (expected after implementation)

- `uv run pytest tests/test_artifact_encryption.py -q`
- `uv run pytest tests/test_fs_permissions.py -q`
- `uv run pytest tests/test_phase2_audit.py tests/test_policy_audit.py -q`
- `uv run pytest tests/test_graph.py tests/test_incremental.py -q`
- `uv run pytest tests/test_wiki.py -q` (if wiki paths touched)
- `uv run code-review-graph verify-policy` (hardened vs standard fixtures in CI)

## Exit Gates

- All listed pytest modules pass.
- At least one test proves **fail-closed** when `require_encryption` and missing key.
- At least one test proves **encrypted write** (or SQLCipher open) for `graph` or file artifacts when key present.
- Permission verification reports stable machine-readable status under hardened_local.
- Audit file contains a recorded denial event for a synthetic encryption-failure scenario.

## Post-Execution

- Promote `status: pending` → `active` during execution; set `status: complete` in `02-VERIFICATION.md` (if created) when phase scorecard passes.

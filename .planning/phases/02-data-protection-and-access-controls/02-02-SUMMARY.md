---
phase: 02-data-protection-and-access-controls
plan: "02"
subsystem: security
tags: [posix, chmod, filesystem, cli]

requires:
  - phase: 01-policy-foundation-and-threat-boundaries
    provides: verify-policy CLI baseline
provides:
  - POSIX 0700/0600 hardening for `.code-review-graph/` under hardened_local
  - Machine-readable filesystem posture in verify-policy JSON and text output
affects: []

tech-stack:
  added: []
  patterns: [resolve_effective_runtime_policy for profile gate]

key-files:
  created:
    - code_review_graph/security/fs_permissions.py
    - tests/test_fs_permissions.py
  modified:
    - code_review_graph/incremental.py
    - code_review_graph/cli.py

key-decisions:
  - "chmod runs only after data dir creation and only when effective policy mode is hardened_local."
  - "Windows: no chmod; verification reports FS_PERMISSIONS_SKIP."

requirements-completed: [REQ-04]

duration: consolidated
completed: "2026-04-29"
---

# Phase 2 Plan 02: Filesystem permissions Summary

**POSIX owner-only modes on the repo data directory for hardened_local, plus verify-policy reporting without breaking non-POSix CI.**

## Accomplishments

- `apply_hardened_data_dir_permissions` sets 0700 on the data dir and 0600 on immediate files (0700 on child dirs).
- `get_data_dir` invokes hardening when `resolve_effective_runtime_policy().mode` is `hardened_local`.
- `verify-policy` adds `filesystem_permissions` with stable keywords (`FS_PERMISSIONS_OK|WARN|SKIP`) and human-readable lines.

## Deviations from Plan

None.

## Self-Check: PASSED

- `pytest tests/test_fs_permissions.py tests/test_incremental.py tests/test_policy_verify.py` passes.

---
phase: 02-data-protection-and-access-controls
plan: "01"
subsystem: security
tags: [fernet, sqlcipher, sqlite, pydantic, encryption]

requires:
  - phase: 01-policy-foundation-and-threat-boundaries
    provides: policy schema, audit baseline, profile resolution
provides:
  - ArtifactEncryptionPolicy on HardenedPolicy
  - SQLCipher-backed GraphStore when enabled with valid Fernet key
  - Encrypted audit JSONL, memory, and wiki payloads under policy
affects: [phase-03-retention]

tech-stack:
  added: [cryptography, sqlcipher3]
  patterns: [resolve_effective_runtime_policy, fail-closed gates, Fernet file envelopes]

key-files:
  created:
    - code_review_graph/security/artifact_crypto.py
    - tests/test_artifact_encryption.py
  modified:
    - code_review_graph/security/policy_schema.py
    - code_review_graph/graph.py
    - code_review_graph/security/audit.py
    - code_review_graph/memory.py
    - code_review_graph/wiki.py
    - pyproject.toml

key-decisions:
  - "SQLCipher uses the same 32-byte secret as the Fernet key (PRAGMA key x'hex')."
  - "Phase 2 security audit lines may emit plaintext JSONL when encryption is required but keys are absent (REQ-06 observability)."

requirements-completed: [REQ-03]

duration: consolidated
completed: "2026-04-29"
---

# Phase 2 Plan 01: Artifact encryption Summary

**Optional Fernet + SQLCipher encryption for graph.db, audit JSONL, memory/, and wiki/ under hardened_local, with fail-closed behavior when require_encryption is set and keys or SQLCipher are unavailable.**

## Performance

- **Tasks:** 3 (schema, crypto/graph integration, audit/memory/wiki wiring)
- **Verification:** `pytest tests/test_artifact_encryption.py tests/test_graph.py tests/test_policy_audit.py tests/test_wiki.py`; targeted security modules pass.

## Accomplishments

- Extended `HardenedPolicy` with strict `ArtifactEncryptionPolicy` (defaults preserve backward compatibility).
- Centralized crypto in `artifact_crypto.py`: Fernet for files, SQLCipher for `graph.db`, `EncryptionRequiredError` for D-03.
- `GraphStore` resolves runtime policy and opens encrypted SQLite when enabled with a valid key.
- Audit, memory, and wiki writers encrypt payloads when `artifact_writes_must_encrypt`; refuse plaintext when policy demands encryption without keys.

## Deviations from Plan

None - plan executed as written (single integration commit in-repo).

## Self-Check: PASSED

- `tests/test_artifact_encryption.py` and integration tests listed above pass locally.

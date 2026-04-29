---
phase: 02
slug: data-protection-and-access-controls
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-29
verified: 2026-04-29
---

# Phase 02 — Security

Security contract for artifact encryption, filesystem permissions for `.code-review-graph/`, and Phase 2 audit expansion (REQ-03, REQ-04, REQ-06).

## Trust boundaries

| Boundary | Description | Data crossing |
|----------|-------------|---------------|
| Env → key loader | Host supplies key material | `CRG_ARTIFACT_ENCRYPTION_KEY` |
| Disk ↔ decrypt | Ciphertext loaded into process memory | Graph DB, memory/wiki files, audit JSONL |
| Local FS ↔ process | Other local principals may access paths | POSIX modes under data dir |
| Audit JSONL → operator | File may be copied off machine | Metadata-only lines |

## Threat register

| Threat ID | Category | Component | Disposition | Mitigation / disposition detail | Status |
|-----------|----------|-----------|-------------|--------------------------------|--------|
| T-02-01 | I | `artifact_crypto.py` key handling | mitigate | Key from env only; no persisted key material in repo paths | **closed** — implementation + `tests/test_artifact_encryption.py` |
| T-02-02 | T | Encrypted JSONL / markdown | mitigate | Fernet AEAD; decrypt failures surfaced | **closed** — `artifact_crypto.py`, tests |
| T-02-03 | E | Missing encryption key | mitigate | `EncryptionRequiredError` / refuse paths when policy requires encryption | **closed** — memory/wiki/graph integration tests |
| T-02-04 | E | `GraphStore` plaintext fallback | mitigate | No silent plaintext when encryption required | **closed** — `tests/test_artifact_encryption.py`, `graph.py` wiring |
| T-02-05 | I | Data dir world-readable | mitigate | `0o700` / `0o600` (POSIX) via `fs_permissions` + `get_data_dir` | **closed** — `tests/test_fs_permissions.py` |
| T-02-06 | E | chmod / checks on wrong path | mitigate | Operations under resolved `get_data_dir`; `_validate_repo_root` pattern in tools | **closed** — `fs_permissions.py`, CLI verify-policy FS block |
| T-02-07 | I | Windows ACL gap | **accept** | Documented limitation vs Unix modes (see Accepted risks) | **closed** — accepted risk |
| T-02-08 | I | Audit metadata leakage | mitigate | `_scrub_metadata`; basename-only path hints | **closed** — `audit.py`, `tests/test_policy_audit.py` |
| T-02-09 | D | Audit log tampering | **accept** | Local append-only JSONL trust model (same as Phase 1); no HMAC in scope | **closed** — accepted risk |
| T-02-10 | E | Missing audit on deny | mitigate | Phase 2 tests assert audit on encryption/permission denial paths | **closed** — `tests/test_phase2_audit.py`, `tests/test_policy_audit.py` |

## Accepted risks log

| Risk ID | Threat ref | Rationale | Accepted by | Date |
|---------|------------|-----------|-------------|------|
| AR-02-01 | T-02-07 | Windows ACL semantics differ from POSIX `0700`/`0600`; product does not claim full Unix-equivalent ACL guarantees in v1. Operators on Windows rely on documented behavior and OS defaults. | Phase 02 plan disposition | 2026-04-29 |
| AR-02-02 | T-02-09 | Tamper detection for local JSONL is out of scope for this phase; threat accepted per plan (same trust model as Phase 1 audit baseline). | Phase 02 plan disposition | 2026-04-29 |

## Security audit trail

| Audit date | Threats total | Closed | Open | Run by |
|------------|---------------|--------|------|--------|
| 2026-04-29 | 10 | 10 | 0 | `/gsd-secure-phase 02` |

## Evidence commands

```bash
uv run pytest tests/test_artifact_encryption.py tests/test_graph.py tests/test_fs_permissions.py \
  tests/test_phase2_audit.py tests/test_policy_audit.py tests/test_policy_verify.py tests/test_wiki.py -q
```

## Sign-off

- [x] Every threat row **closed** (mitigated in code/tests or **accept** with log entry)
- [x] `threats_open: 0`

**Approval:** verified 2026-04-29

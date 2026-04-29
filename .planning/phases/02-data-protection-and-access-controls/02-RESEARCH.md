# Phase 2 Research — Data Protection (Encryption-at-Rest Integration)

**Phase:** 02-data-protection-and-access-controls  
**Sources:** `02-CONTEXT.md` (D-01–D-03), `LOCAL_SECURITY_FOUNDATIONS.md`, Phase 1 policy/audit modules.

## Objective

Define how **optional application-layer encryption** under `hardened_local` integrates with existing persistence paths without breaking offline-first workflows, while honoring **fail-closed** behavior when keys are missing (D-03).

## Canonical Paths (Repo Dot-Directory)

| Artifact | Primary module(s) | Default location |
|----------|-------------------|------------------|
| Graph SQLite | `graph.py` (`GraphStore`), `incremental.get_db_path` | `<data_dir>/graph.db` + WAL/SHM |
| Policy audit JSONL | `security/audit.py` (`resolve_audit_log_path`) | `.code-review-graph/policy_audit.jsonl` (or `CRG_AUDIT_LOG_PATH`) |
| Memory markdown | `memory.py` (`save_result`, `list_memories`) | `<data_dir>/memory/*.md` |
| Wiki markdown | `wiki.generate_wiki`, CLI `wiki` | `<data_dir>/wiki/*.md` |

`get_data_dir` (`incremental.py`) resolves `<data_dir>` as `repo_root/.code-review-graph` unless `CRG_DATA_DIR` overrides.

## Hybrid Model (D-01)

- **Baseline (all users):** Document FDE expectations + filesystem permission hardening (Phase 2 Plan 02); no mandatory app-layer crypto.
- **`hardened_local` + policy:** Optional **artifact encryption** toggled via policy schema and env-supplied key material. When **enabled**, sensitive dot-dir artifacts listed in D-02 must not be written or read as plaintext through protected operations.

## Technical Options

### 1. Non-database files (audit, memory, wiki)

- **`cryptography` + Fernet (AES-128 CBC + HMAC)** — mature wheels, fits append/read patterns with clear failure modes.
- **Per-line JSONL:** Each audit record serialized as JSON, then Fernet-encrypt the line payload (or encode ciphertext as one JSON field). Readers used by tests/verification must decrypt consistently.
- **Markdown trees:** Encrypt file body; preserve optional plaintext metadata only if policy allows (default: treat full file as sensitive when encryption is on).

### 2. SQLite (`graph.db`)

- **SQLCipher-style encryption:** Single key for DB file; matches “encrypt graph.db” literally. Python bindings vary by platform (`sqlcipher3`, `pysqlcipher3`); CI must pin a strategy that builds or skips per matrix with explicit tests.
- **Alternatives (tradeoffs):** Plain `sqlite3` cannot apply transparent SQLCipher PRAGMA key; whole-file copy encrypt/decrypt on each open is incompatible with WAL concurrency — **not** recommended as primary.

**Recommendation:** Prefer **SQLCipher-capable connection** for `GraphStore` when policy requires encryption and key is present; **fail closed** if policy requires encryption but SQLCipher/key path is unavailable (D-03). Document optional extra dependency if native wheels are required.

### 3. Policy and loader

- Extend `HardenedPolicy` with an **`ArtifactEncryptionPolicy`** block: `enabled`, `require_encryption` (fail-closed when true), `key_env_var` (or fixed env name per implementation), optional algorithm/version fields for forward compatibility.
- Reuse **Phase 1** `load_policy` / profile resolution (`CRG_SECURITY_PROFILE`) — encryption gates consult the resolved policy object, not ad hoc globals.

### 4. Fail-closed matrix (D-03)

| Policy state | Key configured | Expected behavior |
|--------------|----------------|-------------------|
| Encryption required | No | Refuse sensitive read/write; emit audit + clear error (no plaintext persistence) |
| Encryption required | Yes | Encrypted I/O for in-scope artifacts |
| Encryption off | Any | Existing plaintext behavior (still subject to REQ-04 permissions) |

## Out of Scope (Per CONTEXT)

- **`~/.code-review-graph` registry encryption** — follow-up unless trivial alignment is discovered during implementation.
- **REQ-05 retention/deletion** — Phase 3.

## Testing Notes

- Unit tests with **temporary dirs** and **in-memory or isolated DB paths**; never rely on developer home directories.
- Windows: permission APIs differ — POSIX `chmod` expectations guarded with skips or capability checks as in existing project patterns.

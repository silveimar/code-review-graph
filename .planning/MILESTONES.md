# Milestones

## v1.0 — Local-Only Security Hardening (shipped 2026-04-30)

**Phases completed:** 6 phases, 14 plans, 16 tasks

**Artifacts:** [Roadmap archive](milestones/v1.0-ROADMAP.md) · [Requirements archive](milestones/v1.0-REQUIREMENTS.md) · [Audit](milestones/v1.0-MILESTONE-AUDIT.md)

**Key accomplishments:**

- Hardened-local policy schema, fail-closed loader, egress guard, embedding enforcement, and offline workflow regression tests.
- Policy audit JSONL (`verify-policy` CLI with deterministic exit codes).
- Optional Fernet + SQLCipher for graph/audit/memory/wiki; POSIX permissions for data dir; audit expansion for encryption and permission events.
- Retention policy model, `cleanup-data` with dry-run default and audit on apply; operator runbook and `verify-policy` retention reporting.
- Phase 4 hardening posture suite (`tests/test_hardening_posture.py`), CI regression documentation, release checklist (REQ-07).
- Formal milestone verification: `03-VERIFICATION.md`, `04-VERIFICATION.md`; REQ-01–REQ-07 traceability signed off.

**Deferred / tech debt (non-blocking):** Multi-root `verify-policy` vs `cleanup-data --repo` parity (optional); `02-VERIFICATION.md` YAML frontmatter cosmetic consistency.

---

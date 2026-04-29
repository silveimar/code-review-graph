# Phase 3 Research — Retention, Deletion, Operational Safety

**Date:** 2026-04-29

## Questions answered

### Where do artifacts live?

- Repo-local **`.code-review-graph/`**: `graph.db`, audit JSONL (via `security/audit.py`), `memory/`, wiki outputs — established in Phase 2 CONTEXT.
- **Multi-repo registry** (`~/.code-review-graph/`): mentioned in Phase 2 as possible follow-up; Phase 3 plans default to **repo dot-dir** unless explicitly extended.

### Existing deletion / purge hooks

- **`memory.py`**: delete-all memories helper — reuse patterns for bulk cleanup.
- **`incremental.py`**: stale node purge when files removed from VCS — **different concern** (graph consistency vs retention policy); do not conflate without explicit task.
- **`refactor.py`**: `_cleanup_expired` — internal refactor cache TTL; **not** user data retention; only reuse naming discipline.

### Policy extension point

- **`HardenedPolicy`** in `policy_schema.py` already holds `egress`, `audit`, `artifact_encryption`. **Retention** belongs as a sibling sub-model (e.g. `RetentionPolicy`) with `extra="forbid"`, optional per-sink `max_age_days` (nullable = unlimited).

### SQLite / encryption interaction

- When **SQLCipher/Fernet** protects `graph.db`, “secure delete” for rows still leaves **page-level** residuals unless VACUUM and optional file-level wipe documented (per D-03 pragmatic stance).

### CLI alignment

- **`verify-policy`** already surfaces JSON blocks — extend with **non-destructive** retention preview (`would_remove` counts).
- Destructive operations belong under a **separate** command (`cleanup` / `prune-data`) with `--dry-run` default or explicit `--apply`.

## Risks

- Accidental data loss if automatic prune defaults are aggressive → **explicit CLI first**, dry-run heavy (CONTEXT D-02/D-03).

## Recommendations for planner

1. Schema-first retention config → evaluation pure function → CLI wires policy loader.
2. Audit emit **cleanup_requested**, **cleanup_completed**, **cleanup_denied** (REQ-06) with outcome counts, not raw paths.

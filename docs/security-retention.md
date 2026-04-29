# Retention and cleanup (operational safety)

This project stores analysis artifacts under `.code-review-graph/` (or `CRG_DATA_DIR`). For **hardened-local** deployments you can cap how long those artifacts remain using optional retention fields in your security policy JSON.

## Configure limits

In your hardened policy file (see `CRG_SECURITY_POLICY_PATH`), set optional `max_age_days` per sink inside `retention`:

| Field | Applies to |
| --- | --- |
| `audit_log` | `policy_audit.jsonl` in the data directory |
| `memory_artifacts` | `memory/*.md` |
| `wiki_outputs` | `wiki/**/*.md` |
| `graph_derived` | `graph.db` and SQLite sidecar files (`-wal`, `-shm`) |

Omitted fields or `null` mean **no limit** for that sink.

## Inspect posture

```bash
code-review-graph verify-policy
code-review-graph verify-policy --json
```

The report includes a **Retention** section with active limits and pointers to cleanup.

## Preview and delete

```bash
# Safe default: list candidates only (no deletes)
code-review-graph cleanup-data

# Same as JSON (for automation)
code-review-graph cleanup-data --json

# Actually remove expired paths (requires explicit flag)
code-review-graph cleanup-data --apply
```

Always review dry-run output before `--apply`.

## Audit trail

Successful applies emit `retention_cleanup` records to the audit log (when auditing is enabled). See REQ-06.

## Residual risks (honest local threat model)

Deletion uses normal file unlink and SQLite file removal. **SSD wear-leveling**, backups, and snapshots can retain data longer than this tool enforces. Full-disk encryption reduces exposure when the machine is powered off. This is **not** a cryptographic wipe.

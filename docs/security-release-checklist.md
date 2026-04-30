# Security release checklist (hardened local)

Use this checklist before declaring a release **ready for local secure usage** against the shipped v1.0 requirements archive (`.planning/milestones/v1.0-REQUIREMENTS.md`). When a new planning milestone adds `.planning/REQUIREMENTS.md`, prefer that file for the latest contract.

**REQ-07** requires an exposed verification path: policy/status checks operators can run (`verify-policy`, JSON contract, automated tests). This doc ties those steps together for releases.

## Automated (required)

1. **Full test suite** — same command CI uses:
   ```bash
   uv run pytest tests/ --tb=short -q --cov=code_review_graph --cov-fail-under=65
   ```
2. **Phase 4 posture orchestration** (subset):
   ```bash
   uv run pytest -m hardening_posture --tb=short -q
   ```
3. **Policy verification (human-readable)**:
   ```bash
   CRG_SECURITY_PROFILE=hardened_local code-review-graph verify-policy
   ```
4. **Policy verification (JSON)** — for tooling / CI audits:
   ```bash
   CRG_SECURITY_PROFILE=hardened_local code-review-graph verify-policy --json
   ```
   Expect `"compliant": true` when using default hardened policy and valid audit log path.

## Configuration sanity

- **`CRG_SECURITY_PROFILE=hardened_local`** for secure workflows.
- Optional **`CRG_SECURITY_POLICY_PATH`** — if set, file must exist and parse as hardened policy.
- **`CRG_AUDIT_LOG_PATH`** — writable path for audit JSONL when auditing is enabled.

## Operational docs

- Retention and cleanup: [security-retention.md](security-retention.md)
- CI expectations: [ci-security-regression.md](ci-security-regression.md)

## Optional manual / platform checks

- Confirm `.code-review-graph/` permissions match your threat model (platform-specific).
- After `cleanup-data --dry-run` / `--apply`, confirm artifacts removed as described in the retention doc.

## References

- Requirements (v1.0): `.planning/milestones/v1.0-REQUIREMENTS.md` (REQ-01–REQ-07)
- Roadmap: `.planning/ROADMAP.md` (milestone index; v1.0 detail in `milestones/v1.0-ROADMAP.md`)

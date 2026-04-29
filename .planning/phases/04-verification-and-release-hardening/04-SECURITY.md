---
phase: 04
slug: verification-and-release-hardening
status: verified
threats_open: 0
asvs_level: 1
created: 2026-04-29
---

# Phase 04 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Dev/CI runner | Host invokes pytest and subprocess CLI tests with repo checkout | Local env vars (`CRG_*`), stdout JSON from `verify-policy --json` |
| Documentation | Operator reads markdown only; no executable trust | Guidance text — sensitivity: operational (non-secret) |
| Same-repo subprocess | `tests/test_hardening_posture.py` spawns interpreter against checked-out tree | No network requirement for posture subprocess path |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-04-01 | Tampering | `tests/test_hardening_posture.py` subprocess | mitigate | `subprocess.run(..., cwd=REPO_ROOT, env=...)` ties CLI to repository root; `sys.executable` avoids PATH hijack for `-m code_review_graph` | closed |
| T-04-02 | Information disclosure | `docs/ci-security-regression.md` | mitigate | Doc lists the same jobs/commands as `.github/workflows/ci.yml` (`lint`, `type-check`, `security`/bandit, `schema-sync`, `test` matrix 3.10–3.13, cov 65%) | closed |
| T-04-03 | Misrepresentation | `docs/security-release-checklist.md` | mitigate | Checklist references `.planning/REQUIREMENTS.md` and REQ-07; does not claim beyond documented controls | closed |

*Disposition: mitigate — controls verified in codebase/docs.*

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-04-29 | 3 | 3 | 0 | gsd-secure-phase (orchestrator) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log (none)
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-04-29

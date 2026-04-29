# Phase 6: Release Phase Formal Verification — Context

**Gathered:** 2026-04-29  
**Status:** Ready for planning  
**Mode:** `[auto]` discuss-phase — single pass

<domain>
## Phase Boundary

Publish **`04-VERIFICATION.md`** under Phase 4’s directory (`.planning/phases/04-verification-and-release-hardening/`) so REQ-01–REQ-04 and REQ-07 have formal milestone traceability aligned with Phase 4 substantive work (`04-01`–`04-03`), `04-VALIDATION.md`, hardening posture tests, CI narrative, and operator docs.

**No new product code** unless verification discovers a doc/test label mismatch requiring a minimal fix.

</domain>

<decisions>
## Decisions

### Document shape

- **D-01 [auto]:** Mirror **`01-VERIFICATION.md`** and **`03-VERIFICATION.md`** — scored truths, roadmap criteria, artifact table, commands from `04-VALIDATION.md` + `tests/test_hardening_posture.py` / `tests/test_phase4_validation.py` as cited in ROADMAP Phase 6 success criteria.

### Scope of REQ rows

- **D-02 [auto]:** Phase 6 formal sign-off covers **REQ-01, REQ-02, REQ-03, REQ-04, REQ-07** per roadmap (Phase 4 requirement rows); REQ-05/REQ-06 already closed in Phase 5 artifact.

### Single plan

- **D-03 [auto]:** One executable plan **06-01** producing **`04-VERIFICATION.md`** plus **REQUIREMENTS.md** row updates for those REQ IDs.

</decisions>

<canonical_refs>
## Canonical References

- `.planning/phases/04-verification-and-release-hardening/04-VALIDATION.md`
- `.planning/phases/04-verification-and-release-hardening/04-01-SUMMARY.md` – `04-03-SUMMARY.md`
- `tests/test_hardening_posture.py`, `tests/test_phase4_validation.py` (if present)
- `docs/security-release-checklist.md`, `docs/ci-security-regression.md`
- `.planning/v1.0-MILESTONE-AUDIT.md`

</canonical_refs>

---

*Phase: 06-release-phase-formal-verification*

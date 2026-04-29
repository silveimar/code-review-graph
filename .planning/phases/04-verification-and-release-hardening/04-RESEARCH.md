# Phase 4 Research: Verification and Release Hardening

## RESEARCH COMPLETE

**Date:** 2026-04-29  
**Question:** What do we need to know to plan end-to-end verification, CI regression hooks, and release artifacts well?

### Findings

1. **Existing pytest security coverage** — `tests/test_policy_verify.py` already exercises `verify-policy` via in-process `main()`; `tests/test_egress_guard.py` covers egress matrix for `hardened_local`; `tests/test_retention_cleanup.py`, `tests/test_artifact_encryption.py` cover REQ-05/REQ-03 paths. Phase 4 should add a **thin orchestration module** (per CONTEXT) that **subprocess-spawns** `python -m code_review_graph verify-policy --json` for realism and **reuses** in-process checks (`resolve_policy_for_profile`, `check_egress`) without duplicating full matrix logic.

2. **CLI entry for subprocess** — `python -m code_review_graph` maps to `cli.main()` (`code_review_graph/__main__.py`). Pass the same env vars as existing verify-policy tests (`CRG_SECURITY_PROFILE`, `CRG_AUDIT_LOG_PATH`, clear `PYTEST_CURRENT_TEST`).

3. **CI** — `.github/workflows/ci.yml` runs lint, mypy, bandit, schema-sync, then pytest with 65% coverage across Python 3.10–3.13. No global `CRG_SECURITY_PROFILE` (tests set env per-case). **Regression integration** = new tests collected by default pytest; optional **pytest marker** `hardening_posture` for filtered local runs.

4. **Docs** — `docs/security-retention.md` exists; add **`docs/security-release-checklist.md`** for REQ-07 operator proof and release acceptance, and index it from `docs/INDEX.md`.

5. **MCP smoke** — CONTEXT defers to discretion; existing `tests/test_main.py` / tools tests cover MCP surfaces. Phase 4 plans **omit** mandatory MCP subprocess smoke unless a gap appears during execution.

### Risks

- **Double runtime** if CI runs hardening file both standalone and in full suite — avoid duplicate steps; single pytest invocation covers all.

---

## Validation Architecture

**Dimension 8 (Nyquist):** Automated verification for Phase 4 is entirely pytest + CI + markdown review.

| Dimension | Mechanism |
|-----------|-----------|
| Correctness | `uv run pytest tests/test_hardening_posture.py -q --tb=short` |
| Regression | Full `uv run pytest tests/ -q` in CI matrix |
| Operator proof | `docs/security-release-checklist.md` + `verify-policy --json` documented |

**Wave 0:** Not required — pytest infrastructure exists (`TESTING.md`).

**Sampling:** After each plan wave, run quick pytest on new/edited tests; before ship, full suite locally.

---
phase: 04
slug: verification-and-release-hardening
status: verified
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-29
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `uv run pytest tests/test_hardening_posture.py tests/test_phase4_validation.py -q --tb=short` |
| **Full suite command** | `uv run pytest tests/ --tb=short -q` |
| **Estimated runtime** | ~60–120 seconds full suite (environment-dependent) |

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_hardening_posture.py tests/test_phase4_validation.py -q --tb=short` when touched
- **After every plan wave:** `uv run pytest tests/ -q --tb=short` (or CI-equivalent)
- **Before `/gsd-verify-work`:** Full suite green
- **Max feedback latency:** &lt; 300 s for full suite locally

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-T1 | 01 | 1 | REQ-01–REQ-07 | T-04-01 | Orchestrated posture checks match hardened_local | integration | `pytest tests/test_hardening_posture.py` | ✅ | ✅ green |
| 04-02-T1 | 02 | 2 | REQ-01–REQ-07 (CI) | — | Marker registered; CI collects tests | unit | `pytest tests/test_phase4_validation.py::test_pyproject_registers_hardening_posture_marker` | ✅ | ✅ green |
| 04-02-T2 | 02 | 2 | REQ-01–REQ-07 (CI) | — | CI regression doc present | unit | `pytest tests/test_phase4_validation.py::test_ci_security_regression_doc_exists_and_links_workflow` | ✅ | ✅ green |
| 04-03-T1 | 03 | 3 | REQ-07 | — | Operator checklist documents verify path | unit | `pytest tests/test_phase4_validation.py::test_security_release_checklist_exists_and_req07` | ✅ | ✅ green |

---

## Wave 0 Requirements

- Existing infrastructure covers phase requirements — no new Wave 0 stubs.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|---------------------|
| Filesystem permission nuances on macOS vs Linux | REQ-04 | Platform-specific umask | Follow checklist “Optional platform checks” in `docs/security-release-checklist.md` |

---

## Validation Audit 2026-04-29

| Metric | Count |
|--------|-------|
| Gaps found | 3 doc/marker rows lacked pytest |
| Resolved | 3 (`tests/test_phase4_validation.py`) |
| Escalated | 0 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity maintained
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** verified 2026-04-29

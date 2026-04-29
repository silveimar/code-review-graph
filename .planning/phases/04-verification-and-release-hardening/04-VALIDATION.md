---
phase: 04
slug: verification-and-release-hardening
status: draft
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
| **Quick run command** | `uv run pytest tests/test_hardening_posture.py -q --tb=short` |
| **Full suite command** | `uv run pytest tests/ --tb=short -q` |
| **Estimated runtime** | ~60–120 seconds full suite (environment-dependent) |

---

## Sampling Rate

- **After every task commit:** `uv run pytest tests/test_hardening_posture.py -q --tb=short` when that file exists/edited
- **After every plan wave:** `uv run pytest tests/ -q --tb=short` (or CI-equivalent)
- **Before `/gsd-verify-work`:** Full suite green
- **Max feedback latency:** &lt; 300 s for full suite locally

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-T1 | 01 | 1 | REQ-01–REQ-07 | T-04-01 | Orchestrated posture checks match hardened_local | integration | `pytest tests/test_hardening_posture.py` | ✅ | ⬜ pending |
| 04-02-T1 | 02 | 2 | REQ-01–REQ-07 (CI) | — | Marker registered; CI collects tests | config | `grep hardening_posture pyproject.toml` | ✅ | ⬜ pending |
| 04-03-T1 | 03 | 3 | REQ-07 | — | Operator checklist documents verify path | doc | `test -f docs/security-release-checklist.md` | ✅ | ⬜ pending |

---

## Wave 0 Requirements

- Existing infrastructure covers phase requirements — no new Wave 0 stubs.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|---------------------|
| Filesystem permission nuances on macOS vs Linux | REQ-04 | Platform-specific umask | Follow checklist “Optional platform checks” |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity maintained
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

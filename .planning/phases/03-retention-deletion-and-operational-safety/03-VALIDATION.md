---
phase: 03
phase_slug: retention-deletion-and-operational-safety
created: 2026-04-29
status: complete
nyquist_compliant: true
wave_0_complete: true
validated: 2026-04-29T23:00:00Z
---

# Phase 03 — Validation Strategy (Retention, Deletion, Operational Safety)

## Validation architecture

- **Objective:** Demonstrate **REQ-05** (retention and secure deletion workflows) and **REQ-06** (audit for cleanup) via automated tests and CLI contracts.
- **Primary gate:** `RetentionPolicy` loads with defaults and forbids unknown keys; cleanup remains **dry-run by default**; **`--apply`** required for deletes.
- **Secondary gate:** `verify-policy` surfaces retention posture (human + JSON) without performing deletion.
- **Tertiary gate:** `cleanup-data --apply` emits `retention_cleanup` audit records when audit sink is active.
- **Evidence model:** pytest modules below + subprocess-style CLI tests via `cli.main`.

## Test infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (project `pyproject.toml` / `uv run pytest`) |
| **Config** | `pyproject.toml`, `pytest.ini` patterns |
| **Quick run (Phase 3 scope)** | `uv run pytest tests/test_retention_policy.py tests/test_retention_cleanup.py tests/test_policy_verify.py -q` |
| **Full security slice** | Add `tests/test_policy_audit.py` when auditing cross-cutting audit behavior |

## Per-plan / task verification map

| Task | Plan | Requirement | Behavior | Automated command | Status |
|------|------|-------------|----------|-------------------|--------|
| Retention schema + defaults | 03-01 | REQ-05 | Optional per-sink `max_age_days`; `extra=forbid` | `uv run pytest tests/test_retention_policy.py -q` | green |
| Loader compatibility | 03-01 | REQ-05 | Policies without `retention` block load | same | green |
| Pure retention evaluation | 03-02 | REQ-05 | Candidates from mtime vs limits; no I/O side effects in eval | `uv run pytest tests/test_retention_cleanup.py -k TestRetentionEval -q` | green |
| cleanup-data CLI | 03-02 | REQ-05, REQ-06 | Dry-run default; `--apply` deletes; audit on apply | `uv run pytest tests/test_retention_cleanup.py -q` | green |
| verify-policy retention section | 03-03 | REQ-05, REQ-06, REQ-07 | JSON includes `retention` keys | `uv run pytest tests/test_policy_verify.py -q` | green |
| Operator runbook | 03-03 | REQ-05 | Doc exists at `docs/security-retention.md` | Manual spot-check (optional) | doc present |

## Dimension coverage

1. **Schema (REQ-05):** `tests/test_retention_policy.py`
2. **Cleanup evaluation + CLI (REQ-05/06):** `tests/test_retention_cleanup.py`
3. **Verification reporting (REQ-07 extension):** `tests/test_policy_verify.py` asserts `retention` in JSON

## Exit gates

- [x] Phase 3 scoped pytest modules pass (see command above).
- [x] No deletion without explicit `--apply` (asserted in cleanup tests).
- [x] `verify-policy --json` includes stable additive `retention` block.

## Manual-only (optional)

| Behavior | Why manual |
|----------|------------|
| Read `docs/security-retention.md` and confirm links from operator workflow | Doc smoke; not pytest-covered |

*No blocking manual-only items — automation covers acceptance paths.*

## Validation audit 2026-04-29

| Metric | Count |
|--------|-------|
| Gaps found (MISSING tests for REQ-05/06 paths) | 0 |
| Resolved | 0 |
| Escalated | 0 |

**Sign-off:** Phase 03 Nyquist reconstruction complete — existing test suite covers declared plans; `nyquist_compliant: true`.

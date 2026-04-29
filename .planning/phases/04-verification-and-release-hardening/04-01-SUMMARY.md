# Plan 04-01 Summary

**Status:** Complete  
**Artifacts:** `tests/test_hardening_posture.py`

- Subprocess: `python -m code_review_graph verify-policy --json` under `hardened_local`.
- In-process: egress deny spot-check aligned with `tests/test_egress_guard.py`.
- Pytest marker: `hardening_posture` (registered in plan 04-02 via `pyproject.toml`).

**Verify:** `uv run pytest tests/test_hardening_posture.py -q`

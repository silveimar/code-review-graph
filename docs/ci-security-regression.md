# CI security regression coverage

This project enforces **local-only hardening** requirements (see the v1.0 archive `.planning/milestones/v1.0-REQUIREMENTS.md`, or a future live `.planning/REQUIREMENTS.md` when the next milestone is defined) through automated checks in GitHub Actions.

## Workflow (`.github/workflows/ci.yml`)

| Job | Purpose |
|-----|---------|
| `lint` | `ruff check code_review_graph/` |
| `type-check` | `mypy code_review_graph/` |
| `security` | `bandit` static analysis |
| `schema-sync` | Python vs VS Code extension SQLite schema version alignment |
| `test` | Matrix Python **3.10–3.13** — full `pytest` with **coverage floor 65%** |

Every PR to `main` must pass **all** jobs. There is no separate “security-only” pytest job by design: **security and hardening tests live in `tests/`** and run under the same matrix as the rest of the suite (see Phase 4 CONTEXT: integrate into the existing `test` job).

## Hardening-focused tests

- **`tests/test_hardening_posture.py`** — subprocess `verify-policy --json` plus in-process egress checks (`@pytest.mark.hardening_posture`).
- Other modules: `tests/test_policy_verify.py`, `tests/test_egress_guard.py`, `tests/test_retention_cleanup.py`, `tests/test_artifact_encryption.py`, etc.

### Run only posture orchestration locally

```bash
uv run pytest -m hardening_posture --tb=short -q
```

### Full suite (matches CI)

```bash
uv run pytest tests/ --tb=short -q --cov=code_review_graph --cov-report=term-missing --cov-fail-under=65
```

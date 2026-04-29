# Coding Conventions

**Analysis Date:** Wednesday Apr 29, 2026

## Naming Patterns

**Files:**
- Use `snake_case.py` module names in `code_review_graph/` (for example `code_review_graph/tsconfig_resolver.py`, `code_review_graph/tools/community_tools.py`).
- Keep test files as `test_*.py` under `tests/` (for example `tests/test_parser.py`, `tests/test_tools.py`).
- Avoid creating duplicate suffixed files like `* 2.py` that appear in this repo (`tests/test_main 2.py`, `code_review_graph/memory 2.py`).

**Functions:**
- Use `snake_case` for functions/methods (`code_review_graph/graph.py`, `code_review_graph/cli.py`).
- Prefix test functions with `test_` and keep behavior-focused names (`tests/test_parser.py`).

**Variables:**
- Use lowercase snake_case for local variables (`repo_root`, `db_path`, `line_start`) in `code_review_graph/cli.py` and `code_review_graph/graph.py`.
- Use uppercase constants for module-level immutable values (`_SCHEMA_SQL` in `code_review_graph/graph.py`).

**Types:**
- Use typed dataclasses for structured domain records (`GraphNode`, `GraphEdge`, `GraphStats` in `code_review_graph/graph.py`).
- Use modern Python typing with built-ins and unions (`dict[str, Any]`, `str | Path`) across `code_review_graph/`.

## Code Style

**Formatting:**
- Tool used: Ruff (`[tool.ruff]` in `pyproject.toml`).
- Key settings: line length 100, Python target `py310`, excludes for generated/fixture-heavy files (`pyproject.toml`).

**Linting:**
- Tool used: Ruff with rules `E,F,I,N,W` (`[tool.ruff.lint]` in `pyproject.toml`).
- CI gate: `ruff check code_review_graph/` in `.github/workflows/ci.yml`.
- Use per-file ignores only for justified edge files (`code_review_graph/visualization.py`, fixture notebooks in `pyproject.toml`).

## Import Organization

**Order:**
1. Future imports first (`from __future__ import annotations`) as used in `code_review_graph/cli.py` and `code_review_graph/graph.py`.
2. Standard library imports grouped next (`argparse`, `json`, `pathlib` in `code_review_graph/cli.py`).
3. Third-party imports before local package imports (`networkx` then `from .constants ...` in `code_review_graph/graph.py`).

**Path Aliases:**
- Not applicable for Python package code; use explicit relative package imports (`from .tools...`, `from ..graph...`) in `code_review_graph/`.

## Error Handling

**Patterns:**
- Catch specific exceptions and provide controlled fallback (`PackageNotFoundError` in `code_review_graph/cli.py`).
- Validate inputs early and raise `ValueError` with actionable messages (`_validate_repo_root` in `code_review_graph/tools/_common.py`).
- Use non-throwing cleanup in tests (`Path(...).unlink(missing_ok=True)` in `tests/test_tools.py`, `tests/test_fts_sync.py`).

## Logging

**Framework:** `logging`

**Patterns:**
- Define per-module logger via `logging.getLogger(__name__)` (`code_review_graph/cli.py`, `code_review_graph/graph.py`).
- Prefer logger calls for diagnostics, avoid ad-hoc prints in library code (`code_review_graph/cli.py` keeps `print` for CLI UX only).

## Comments

**When to Comment:**
- Add short rationale comments for non-obvious constraints (for example transaction mode comment in `code_review_graph/graph.py`, stdio safety note in `code_review_graph/cli.py`).
- Keep implementation comments focused on intent and invariants, not trivial restatements.

**JSDoc/TSDoc:**
- Not applicable; codebase conventions rely on Python docstrings.

## Function Design

**Size:** Keep user-facing functions small and delegated; move reusable logic into helper functions (`code_review_graph/tools/_common.py`, `code_review_graph/cli.py`).

**Parameters:** Prefer typed, explicit arguments with sensible defaults (`compact_response(..., detail_level: str = "minimal")` in `code_review_graph/tools/_common.py`).

**Return Values:** Return structured dictionaries for tool responses with stable keys (`status`, `summary`, optional metadata) in `code_review_graph/tools/_common.py`.

## Module Design

**Exports:**
- Use explicit export surfaces through `__all__` for tool modules (`code_review_graph/tools/__init__.py`).
- Keep core behavior in focused modules (`code_review_graph/graph.py`, `code_review_graph/parser.py`) and re-export through package entry modules where needed.

**Barrel Files:**
- Use barrel-style re-export module at `code_review_graph/tools/__init__.py` for MCP tool API composition.

## Quality Gates

- Run lint gate: `ruff check code_review_graph/` (`.github/workflows/ci.yml`).
- Run type gate: `mypy code_review_graph/ --ignore-missing-imports --no-strict-optional` (`.github/workflows/ci.yml`).
- Run security gate: `bandit -r code_review_graph/ -c pyproject.toml` (`.github/workflows/ci.yml`).
- Run test gate with coverage floor: `pytest --tb=short -q --cov=code_review_graph --cov-report=term-missing --cov-fail-under=65` (`.github/workflows/ci.yml`).
- Local contributor baseline mirrors these via `uv run` commands in `CONTRIBUTING.md`.

---

*Convention analysis: Wednesday Apr 29, 2026*

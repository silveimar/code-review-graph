# Testing Patterns

**Analysis Date:** Wednesday Apr 29, 2026

## Test Framework

**Runner:**
- Pytest (configured via `[tool.pytest.ini_options]` in `pyproject.toml`).
- Config: `pyproject.toml` (`testpaths = ["tests"]`, `asyncio_mode = "auto"`, `norecursedirs = ["tests/fixtures"]`).

**Assertion Library:**
- Native `pytest` assertions (plain `assert` style used throughout `tests/test_parser.py`, `tests/test_tools.py`, `tests/test_flows.py`).

**Run Commands:**
```bash
uv run pytest tests/ --tb=short -q                     # Run all tests
uv run pytest tests/test_parser.py -v                  # Run one module
uv run pytest --cov=code_review_graph --cov-report=term-missing --cov-fail-under=50  # Local coverage gate
```

## Test File Organization

**Location:**
- Keep tests in top-level `tests/` with language/feature fixtures in `tests/fixtures/`.
- Keep fixture-only files out of discovery using `norecursedirs = ["tests/fixtures"]` in `pyproject.toml`.

**Naming:**
- Use `test_*.py` naming (`tests/test_graph.py`, `tests/test_incremental.py`, `tests/test_tsconfig_resolver.py`).

**Structure:**
```
tests/
├── test_*.py                  # Behavioral unit/integration tests
├── fixtures/                  # Source samples and parser fixtures
└── (class-based and function-based suites mixed)
```

## Test Structure

**Suite Organization:**
```python
class TestTools:
    def setup_method(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.store = GraphStore(self.tmp.name)

    def teardown_method(self):
        self.store.close()
        Path(self.tmp.name).unlink(missing_ok=True)
```

**Patterns:**
- Use class-scoped setup/teardown when tests share temporary DB setup (`tests/test_tools.py`, `tests/test_graph.py`).
- Use function fixtures for reusable setup with `yield` cleanup (`tests/test_fts_sync.py`).
- Prefer direct, behavior-level asserts over helper wrappers (`tests/test_parser.py`, `tests/test_main.py`).

## Mocking

**Framework:** Pytest fixture tools (`monkeypatch`) plus lightweight in-memory/temporary resources.

**Patterns:**
```python
@pytest.mark.asyncio
async def test_filter_via_env_var(self, monkeypatch):
    monkeypatch.setenv("CRG_TOOLS", "query_graph_tool")
    crg_main._apply_tool_filter(None)
    remaining = set((await crg_main.mcp.get_tools()).keys())
    assert remaining == {"query_graph_tool"}
```

**What to Mock:**
- Environment variables and process-adjacent settings (`tests/test_main.py`).
- Temporary filesystem/database resources rather than production services (`tests/test_tools.py`, `tests/test_refactor.py`).

**What NOT to Mock:**
- Core graph/query logic; tests instantiate real `GraphStore` and run real SQL behavior (`tests/test_graph.py`, `tests/test_fts_sync.py`).

## Fixtures and Factories

**Test Data:**
```python
node1 = NodeInfo(
    kind="Function", name="calculate_total", file_path="app.py",
    line_start=1, line_end=5, language="python",
)
store.store_file_nodes_edges("app.py", [node1], [])
```

**Location:**
- Inline factories and seed helpers inside test modules (`tests/test_tools.py`, `tests/test_fts_sync.py`).
- Static parser fixtures in `tests/fixtures/` (for example `tests/fixtures/sample_python.py`, `tests/fixtures/sample.dart`).

## Coverage

**Requirements:** Coverage threshold enforced in CI at 65% (`.github/workflows/ci.yml`), with local contributor guidance at 50% (`CONTRIBUTING.md`).

**View Coverage:**
```bash
pytest --tb=short -q --cov=code_review_graph --cov-report=term-missing --cov-fail-under=65
```

## Test Types

**Unit Tests:**
- Dominant pattern; validate parser, graph storage, search, and tool behavior in isolation (`tests/test_parser.py`, `tests/test_graph.py`, `tests/test_search.py`).

**Integration Tests:**
- Present for end-to-end graph/update/repository flows (`tests/test_integration_v2.py`, `tests/test_integration_git.py`, `tests/test_daemon.py`).

**E2E Tests:**
- Not detected as browser/UI E2E; project scope is library/CLI/server testing.

## Common Patterns

**Async Testing:**
```python
@pytest.mark.asyncio
async def test_whitespace_handling(self):
    crg_main._apply_tool_filter(" query_graph_tool , semantic_search_nodes_tool ")
    remaining = set((await crg_main.mcp.get_tools()).keys())
    assert remaining == {"query_graph_tool", "semantic_search_nodes_tool"}
```

**Error Testing:**
```python
def test_detect_language_unknown(self):
    assert self.parser.detect_language(Path("foo.txt")) is None
```

## Coverage Shape and Strategy

- Prioritize parser correctness and language breadth in `tests/test_parser.py` and `tests/test_multilang.py`.
- Keep storage/query correctness covered with SQLite-backed tests in `tests/test_graph.py`, `tests/test_transactions.py`, `tests/test_fts_sync.py`.
- Keep tool contract behavior covered in `tests/test_tools.py`, `tests/test_main.py`, and `tests/test_prompts.py`.
- Keep migration/registry/release safety covered in `tests/test_migrations.py`, `tests/test_registry.py`, and CI schema sync checks in `.github/workflows/ci.yml`.

---

*Testing analysis: Wednesday Apr 29, 2026*

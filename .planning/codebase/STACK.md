# Technology Stack

**Analysis Date:** 2026-04-29

## Languages

**Primary:**
- Python 3.10+ - Core CLI, MCP server, parser, graph engine in `code_review_graph/` (`pyproject.toml`, `code_review_graph/main.py`)

**Secondary:**
- TypeScript (extension) - VS Code integration in `code-review-graph-vscode/src/` (`code-review-graph-vscode/package.json`)
- JavaScript (build scripts) - Extension bundling via `esbuild.mjs` (`code-review-graph-vscode/package.json`)

## Runtime

**Environment:**
- Python >=3.10 (`pyproject.toml`, `uv.lock`)
- Node.js runtime via VS Code extension host (`code-review-graph-vscode/package.json`)

**Package Manager:**
- Python: `uv` lockfile workflow (`uv.lock`) and `pip` install paths in CI (`.github/workflows/ci.yml`)
- Node: npm ecosystem for extension deps (`code-review-graph-vscode/package.json`)
- Lockfile: present (`uv.lock`)

## Frameworks

**Core:**
- `fastmcp>=3.2.4` - MCP server framework (`pyproject.toml`, `code_review_graph/main.py`)
- `mcp>=1.0.0,<2` - MCP protocol package (`pyproject.toml`)
- `tree-sitter` + `tree-sitter-language-pack` - Multi-language parsing (`pyproject.toml`, `README.md`)
- SQLite + `networkx` - Graph persistence + in-memory graph ops (`code_review_graph/graph.py`, `pyproject.toml`)

**Testing:**
- `pytest` / `pytest-asyncio` / `pytest-cov` (`pyproject.toml`, `.github/workflows/ci.yml`)

**Build/Dev:**
- `hatchling` - Python build backend (`pyproject.toml`)
- `ruff` - linting (`pyproject.toml`, `.github/workflows/ci.yml`)
- `mypy` - type-checking (`.github/workflows/ci.yml`)
- `bandit` - security scanning (`.github/workflows/ci.yml`)
- `esbuild` + `typescript` - VS Code extension build (`code-review-graph-vscode/package.json`)

## Key Dependencies

**Critical:**
- `fastmcp` - exposes graph tools/prompts over MCP (`pyproject.toml`, `code_review_graph/main.py`)
- `tree-sitter-language-pack` - language grammar support for parsing (`pyproject.toml`)
- `watchdog` - file watch/incremental updates (`pyproject.toml`)
- `networkx` - graph analytics cache paths (`pyproject.toml`, `code_review_graph/graph.py`)

**Infrastructure:**
- `sqlite3` (stdlib) - graph DB and metadata storage (`code_review_graph/graph.py`, `code_review_graph/registry.py`)
- `better-sqlite3` - read-only DB access in extension (`code-review-graph-vscode/package.json`, `code-review-graph-vscode/src/backend/sqlite.ts`)
- `d3` - graph visualization in extension (`code-review-graph-vscode/package.json`)

## Configuration

**Environment:**
- Configured via `CRG_*` variables in runtime code (examples: `CRG_REPO_ROOT`, `CRG_DATA_DIR`, `CRG_GIT_TIMEOUT`, `CRG_TOOLS`) in `code_review_graph/incremental.py`, `code_review_graph/main.py`, `code_review_graph/constants.py`
- Embedding provider vars: `CRG_EMBEDDING_MODEL`, `CRG_OPENAI_API_KEY`, `CRG_OPENAI_BASE_URL`, `CRG_OPENAI_MODEL`, `MINIMAX_API_KEY`, `GOOGLE_API_KEY` in `code_review_graph/embeddings.py`
- `.env*` files not detected at repo root (scan result)

**Build:**
- Python packaging/build: `pyproject.toml`
- Python dependency lock: `uv.lock`
- CI and publish pipelines: `.github/workflows/ci.yml`, `.github/workflows/publish.yml`
- VS Code extension packaging/build: `code-review-graph-vscode/package.json`

## Platform Requirements

**Development:**
- Python 3.10+ and pip/uv-compatible tooling (`pyproject.toml`, `README.md`)
- Optional Node toolchain for extension work (`code-review-graph-vscode/package.json`)

**Production:**
- Primary distribution target: PyPI package + local stdio/HTTP MCP server execution (`.github/workflows/publish.yml`, `code_review_graph/cli.py`)
- Optional deployment surface: VS Code extension consuming local graph DB (`code-review-graph-vscode/src/backend/sqlite.ts`)

---

*Stack analysis: 2026-04-29*

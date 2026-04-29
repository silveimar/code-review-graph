# Codebase Structure

**Analysis Date:** 2026-04-29

## Directory Layout

```text
code-review-graph/
├── code_review_graph/         # Python core package (CLI, MCP server, parser, graph, analysis)
├── code_review_graph/tools/   # Tool-oriented facade modules (build/query/review/community/etc.)
├── code-review-graph-vscode/  # VS Code extension (TypeScript UI + local DB reader)
├── tests/                     # Pytest test suite and fixtures
├── docs/                      # User and operator documentation
├── hooks/                     # Hook scripts and hook config
├── skills/                    # Prompt/skill command artifacts
├── diagrams/                  # Images and visual assets used by docs
├── pyproject.toml             # Python package/build/lint/test config
└── uv.lock                    # Dependency lockfile
```

## Directory Purposes

**`code_review_graph/`:**
- Purpose: Primary runtime package for graph build/query/update and MCP serving.
- Contains: Entry points (`cli.py`, `main.py`), storage (`graph.py`), parsing (`parser.py`), analysis modules.
- Key files: `code_review_graph/cli.py`, `code_review_graph/main.py`, `code_review_graph/graph.py`, `code_review_graph/incremental.py`.

**`code_review_graph/tools/`:**
- Purpose: Public tool contract grouped by capability and consumed by MCP/CLI.
- Contains: Build, query, review, flow, community, docs, registry and refactor adapters.
- Key files: `code_review_graph/tools/__init__.py`, `code_review_graph/tools/build.py`, `code_review_graph/tools/query.py`.

**`code-review-graph-vscode/`:**
- Purpose: IDE integration that reads graph DB and surfaces graph workflows in VS Code.
- Contains: Extension bootstrap, command handlers, SQLite reader, webview/tree UI.
- Key files: `code-review-graph-vscode/src/extension.ts`, `code-review-graph-vscode/src/backend/sqlite.ts`.

**`tests/`:**
- Purpose: Functional and integration verification across parser, graph, tools, and workflows.
- Contains: `test_*.py` modules plus fixtures.
- Key files: `tests/test_tools.py`, `tests/test_graph.py`, `tests/test_incremental.py`.

**`docs/`:**
- Purpose: End-user docs and command references.
- Contains: Usage, troubleshooting, commands, architecture docs.
- Key files: `docs/INDEX.md`, `docs/USAGE.md`, `docs/COMMANDS.md`.

## Key File Locations

**Entry Points:**
- `code_review_graph/cli.py`: CLI command parser and dispatcher.
- `code_review_graph/main.py`: MCP server tool/prompt registration and transport startup.
- `code-review-graph-vscode/src/extension.ts`: VS Code extension activation and command wiring.

**Configuration:**
- `pyproject.toml`: Packaging, dependencies, scripts, ruff, pytest, bandit config.
- `uv.lock`: Resolved dependency lock.
- `hooks/hooks.json`: Hook definitions.

**Core Logic:**
- `code_review_graph/parser.py`: Tree-sitter AST extraction to graph entities.
- `code_review_graph/graph.py`: SQLite schema + graph query engine.
- `code_review_graph/incremental.py`: full/incremental build and watch loops.
- `code_review_graph/changes.py`: diff-to-risk mapping for review guidance.

**Testing:**
- `tests/`: Primary test package.
- `tests/fixtures/`: Sample source fixtures for language and parser coverage.

## Naming Conventions

**Files:**
- Python modules use `snake_case.py` (`incremental.py`, `tsconfig_resolver.py`).
- Test files use `test_*.py` in `tests/` (`test_parser.py`, `test_prompts.py`).
- TypeScript extension files use `camelCase.ts` under feature folders (`treeView.ts`, `statusBar.ts`).

**Directories:**
- Python package directories are `snake_case` (`code_review_graph`).
- Frontend extension directory uses kebab-case package root (`code-review-graph-vscode`) with nested concern folders (`backend`, `features`, `views`, `webview`).

## Where to Add New Code

**New Feature:**
- Primary code: `code_review_graph/` for runtime logic or `code_review_graph/tools/` for a new MCP/CLI-exposed capability.
- Tests: `tests/test_<feature>.py` with fixture additions in `tests/fixtures/` when parsing behavior changes.

**New Component/Module:**
- Implementation: Put core domain modules in `code_review_graph/` and wire exported tool wrappers in `code_review_graph/tools/__init__.py`.

**Utilities:**
- Shared helpers: `code_review_graph/tools/_common.py` for tool-scoped helpers, or dedicated module in `code_review_graph/` if reused across CLI/MCP/analysis.

## Special Directories

**`.code-review-graph/`:**
- Purpose: Runtime data directory containing `graph.db`, generated outputs, and wiki artifacts.
- Generated: Yes.
- Committed: No (ignored by project setup).

**`code-review-graph-vscode/dist/` (from package scripts):**
- Purpose: Built extension output.
- Generated: Yes.
- Committed: Depends on release workflow; source of truth remains `code-review-graph-vscode/src/`.

**`skills/`:**
- Purpose: Skill prompt command packs consumed by supported AI tooling.
- Generated: Tool-assisted; can be regenerated from install flows.
- Committed: Yes.

---

*Structure analysis: 2026-04-29*

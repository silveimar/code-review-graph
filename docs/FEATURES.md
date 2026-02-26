# Features

## v1.5.0 (Current)
- **File organization**: Generated files moved into `.code-review-graph/` directory (auto-created `.gitignore`, legacy migration)
- **Visualization density**: Starts collapsed (File nodes only), search bar, clickable edge type toggles, scale-aware layout for large graphs
- **Project cleanup**: Removed redundant `references/`, `agents/`, `settings.json`

## v1.4.0
- **`init` command**: Automatic `.mcp.json` setup for Claude Code integration
- **Interactive D3.js graph visualization**: `code-review-graph visualize` generates an HTML graph you can explore in-browser
- **Documentation overhaul**: Comprehensive docs audit across all reference files

## v1.3.0
- **Python version check with Docker fallback**: Automatically detects Python 3.10+ and suggests Docker if unavailable
- **Universal install**: `pip install code-review-graph` — no git clone needed
- **CLI entry point**: `code-review-graph` command available system-wide after pip install

## v1.2.0
- **Logging improvements**: Structured logging throughout the codebase
- **Watch debounce**: Smarter file-change detection in watch mode
- **tools.py fixes**: Bug fixes and reliability improvements for MCP tools
- **CI coverage**: GitHub Actions CI/CD pipeline with test coverage reporting

## v1.1.0
- **Watch mode**: `code-review-graph watch` — auto-rebuilds graph on file changes
- **Vector embeddings**: Optional `pip install .[embeddings]` for semantic code search
- **Go, Rust, Java verified**: 12+ languages with dedicated test coverage
- **47 tests passing**, 8 MCP tools registered
- README badges and cleaner install flow

## v1.0.0 (Foundation)
- **Persistent SQLite knowledge graph** — zero external dependencies
- **Tree-sitter multi-language parsing** — classes, functions, imports, calls, inheritance
- **Incremental updates** via `git diff` + automatic dependency cascade
- **Impact-radius / blast-radius analysis** — BFS through call/import/inheritance graph
- **6 MCP tools** for full graph interaction
- **3 review-first skills**: build-graph, review-delta, review-pr
- **PostEdit/PostGit hooks** for automatic background updates
- **FastMCP 3.0 compatible** stdio MCP server

## Privacy & Data
- All data stays 100% local
- Graph stored in `.code-review-graph/graph.db` (SQLite), auto-gitignored
- No telemetry, no network calls
- Respects `.gitignore` and `.code-review-graphignore`

<!-- refreshed: 2026-04-29 -->
# Architecture

**Analysis Date:** 2026-04-29

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                 Interfaces & Entry Surfaces                 │
├──────────────────┬──────────────────┬───────────────────────┤
│   CLI Surface    │    MCP Server    │    VS Code Extension  │
│ `code_review_    │ `code_review_    │ `code-review-graph-   │
│ graph/cli.py`    │ graph/main.py`   │ vscode/src/extension.ts` |
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                Orchestration & Analysis Layer              │
│ `code_review_graph/incremental.py`                         │
│ `code_review_graph/tools/*.py`                             │
│ `code_review_graph/changes.py`, `flows.py`, `communities.py` |
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                Parse/Store/Query Data Plane                │
│ `code_review_graph/parser.py` + `code_review_graph/graph.py` |
│ SQLite DB: `.code-review-graph/graph.db`                   │
└─────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| CLI command router | Parses commands, dispatches build/update/serve/watch/daemon flows | `code_review_graph/cli.py` |
| MCP transport adapter | Registers MCP tools/prompts and binds to stdio/HTTP | `code_review_graph/main.py` |
| Build/update pipeline | Full and incremental graph refresh; watcher and VCS integration | `code_review_graph/incremental.py` |
| Graph persistence layer | SQLite schema, upsert/query API, impact BFS, stats | `code_review_graph/graph.py` |
| Language parser | Tree-sitter parsing and node/edge extraction for supported languages | `code_review_graph/parser.py` |
| Domain analyzers | Risk (`changes`), flows (`flows`), communities (`communities`) | `code_review_graph/changes.py`, `code_review_graph/flows.py`, `code_review_graph/communities.py` |
| Tool façade | Stable tool-level API split by concern (build/query/review/refactor/etc.) | `code_review_graph/tools/__init__.py`, `code_review_graph/tools/*.py` |
| VS Code client | Reads graph DB and exposes tree/webview/commands in IDE | `code-review-graph-vscode/src/extension.ts` |

## Pattern Overview

**Overall:** Layered pipeline with adapter/facade boundaries

**Key Characteristics:**
- Entry adapters (`cli.py`, `main.py`, extension) stay thin and delegate to domain modules.
- Domain services are decomposed by capability (build, query, review, flows, communities, refactor).
- Persistence is centralized in `GraphStore` (`graph.py`) with explicit transaction boundaries.

## Layers

**Entry Layer:**
- Purpose: Expose runtime interfaces (CLI commands, MCP tools/prompts, VS Code commands).
- Location: `code_review_graph/cli.py`, `code_review_graph/main.py`, `code-review-graph-vscode/src/extension.ts`
- Contains: Argument parsing, command handlers, MCP tool registration, IDE command bindings.
- Depends on: Tools API and incremental/build services.
- Used by: End users, AI clients via MCP, VS Code UI.

**Orchestration Layer:**
- Purpose: Coordinate graph build/update, post-processing, and higher-level analysis.
- Location: `code_review_graph/tools/build.py`, `code_review_graph/incremental.py`, `code_review_graph/tools/review.py`
- Contains: Full/incremental updates, changed-file detection, review context composition.
- Depends on: `GraphStore`, parser, analysis modules.
- Used by: CLI commands and MCP tools.

**Analysis Layer:**
- Purpose: Compute specialized insights from graph state.
- Location: `code_review_graph/changes.py`, `code_review_graph/flows.py`, `code_review_graph/communities.py`, `code_review_graph/refactor.py`
- Contains: Risk scoring, affected flow tracing, community clustering, refactor previews.
- Depends on: `GraphStore` read/query APIs.
- Used by: MCP tools, CLI `detect-changes`, post-processing.

**Data Layer:**
- Purpose: Parse source and persist/query structural graph.
- Location: `code_review_graph/parser.py`, `code_review_graph/graph.py`, `.code-review-graph/graph.db`
- Contains: Tree-sitter extraction, schema management, graph traversals, metadata.
- Depends on: SQLite, networkx, language parsers.
- Used by: All orchestration/analysis modules.

## Data Flow

### Primary Request Path

1. CLI/MCP entry receives command/tool invocation (`code_review_graph/cli.py`, `code_review_graph/main.py`).
2. Build/query/review handler resolves repo root and opens store (`code_review_graph/tools/_common.py`, `code_review_graph/tools/build.py`).
3. Parser/update pipeline computes nodes+edges for changed/full file set (`code_review_graph/incremental.py`, `code_review_graph/parser.py`).
4. Store writes atomically and post-processing updates summaries/flows/communities (`code_review_graph/graph.py`, `code_review_graph/tools/build.py`).
5. Tool returns serialized response for CLI JSON output or MCP transport (`code_review_graph/tools/*.py`, `code_review_graph/main.py`).

### VS Code Interaction Flow

1. Extension activates on workspace graph DB presence (`code-review-graph-vscode/src/extension.ts`).
2. `SqliteReader` opens `.code-review-graph/graph.db` and tree providers populate UI (`code-review-graph-vscode/src/backend/sqlite.ts`, `code-review-graph-vscode/src/views/treeView.ts`).
3. User actions trigger CLI wrappers for build/update/review and refresh local views (`code-review-graph-vscode/src/backend/cli.ts`, `code-review-graph-vscode/src/extension.ts`).

**State Management:**
- Persistent state is SQLite-first (`.code-review-graph/graph.db`).
- Runtime caches are in-process (`GraphStore._nxg_cache` in `code_review_graph/graph.py`).
- Metadata (e.g., schema/version/last updated) is stored in DB `metadata` table.

## Key Abstractions

**GraphStore:**
- Purpose: Single API for node/edge persistence and graph queries.
- Examples: `code_review_graph/graph.py`
- Pattern: Repository + query service with explicit transaction control.

**Tool Modules:**
- Purpose: Stable, composable interface layer between transports and core logic.
- Examples: `code_review_graph/tools/build.py`, `code_review_graph/tools/query.py`, `code_review_graph/tools/review.py`
- Pattern: Domain facade split by concern.

**Incremental Update Engine:**
- Purpose: VCS-aware change detection and minimal re-parse strategy.
- Examples: `code_review_graph/incremental.py`
- Pattern: Change-driven pipeline with dependency expansion.

## Entry Points

**CLI Binary Entry:**
- Location: `code_review_graph/cli.py`, `code_review_graph/__main__.py`
- Triggers: `code-review-graph ...` and `crg-daemon ...` scripts from `pyproject.toml`.
- Responsibilities: Command parsing, mode dispatch, output formatting.

**MCP Server Entry:**
- Location: `code_review_graph/main.py`
- Triggers: `code-review-graph serve` (stdio) or `--http`.
- Responsibilities: Tool registration, transport setup, repo-root scoping.

**VS Code Extension Entry:**
- Location: `code-review-graph-vscode/src/extension.ts`
- Triggers: `workspaceContains:.code-review-graph/graph.db` and contributed commands.
- Responsibilities: IDE UI wiring, command execution, DB-backed exploration.

## Architectural Constraints

- **Threading:** Single-threaded request handling at transport edge; heavy work offloaded via `asyncio.to_thread` in MCP tools and `ProcessPoolExecutor` in parse path (`code_review_graph/main.py`, `code_review_graph/incremental.py`).
- **Global state:** Module-level default repo root for MCP resolution (`code_review_graph/main.py`), shared SQLite connection per `GraphStore` instance (`code_review_graph/graph.py`).
- **Circular imports:** Avoid by keeping tool facades in `code_review_graph/tools/*` and importing domain modules inside function scope where needed (`code_review_graph/tools/build.py`).
- **Storage contract:** All higher layers assume `.code-review-graph/graph.db` schema migrations are applied by `GraphStore` init (`code_review_graph/graph.py`, `code_review_graph/migrations.py`).

## Anti-Patterns

### Direct Internal Connection Coupling

**What happens:** Analysis modules directly use `store._conn` for multi-statement operations.
**Why it's wrong:** Bypasses `GraphStore` encapsulation and makes schema-layer changes riskier.
**Do this instead:** Add explicit `GraphStore` APIs for community/flow summary writes, then consume those APIs from `code_review_graph/communities.py` and `code_review_graph/flows.py`.

### Duplicate Variant Files In Package Root

**What happens:** Multiple suffixed variants exist (e.g., `analysis 2.py`, `memory 3.py`, `exports 2.py`) alongside canonical modules.
**Why it's wrong:** Increases ambiguity about active module boundaries and review targets.
**Do this instead:** Keep a single canonical module per concern in `code_review_graph/` and move experiments to a dedicated scratch directory.

## Error Handling

**Strategy:** Fail soft in optional post-processing; fail explicit for core command errors.

**Patterns:**
- Defensive `try/except` around optional analyzers and indexes with warnings (`code_review_graph/tools/build.py`).
- Guarded subprocess calls and invalid-ref rejection before VCS operations (`code_review_graph/incremental.py`, `code_review_graph/changes.py`).

## Cross-Cutting Concerns

**Logging:** Module-level loggers used across CLI/build/analysis paths (`code_review_graph/*.py`).
**Validation:** Repo-root validation and safe ref regex checks (`code_review_graph/tools/_common.py`, `code_review_graph/changes.py`).
**Authentication:** No internal auth subsystem; external integrations rely on host environment variables and platform setup (`pyproject.toml`, `README.md`).

---

*Architecture analysis: 2026-04-29*

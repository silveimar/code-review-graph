# code-review-graph

**Persistent incremental knowledge graph for token-efficient, context-aware code reviews with Claude Code.**

[![GitHub stars](https://img.shields.io/github/stars/tirth8205/code-review-graph?style=flat-square)](https://github.com/tirth8205/code-review-graph/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/tirth8205/code-review-graph/actions/workflows/ci.yml/badge.svg)](https://github.com/tirth8205/code-review-graph/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg?style=flat-square)](https://modelcontextprotocol.io/)
[![v1.5.0](https://img.shields.io/badge/version-1.5.0-purple.svg?style=flat-square)](#)

---

> It turns Claude from "smart but forgetful tourist" into "local expert who already knows the map."

Stop re-scanning your entire codebase on every review. `code-review-graph` builds a structural graph of your code using Tree-sitter, tracks it incrementally, and gives Claude Code the context it needs to review only what changed — and everything affected by those changes.

| Without graph | With graph |
|---|---|
| Full repo scan every review | Only changed + impacted files |
| No blast-radius awareness | Automatic impact analysis |
| Token-heavy (entire codebase) | **5-10x fewer tokens** per review |
| Manual "what else does this affect?" | Graph-powered dependency tracing |

---

## ✨ Features

- **Incremental updates** — Only re-parses files that changed since last build. Subsequent updates take <2s.
- **12+ languages** — Python, TypeScript, JavaScript, Go, Rust, Java, C#, Ruby, Kotlin, Swift, PHP, C/C++
- **Blast-radius analysis** — See exactly which functions, classes, and files are impacted by any change
- **Token-efficient reviews** — Send only changed + impacted code to the model, not your entire repo
- **Auto-update hooks** — Graph stays current on every file edit and git commit
- **Vector embeddings** — Optional semantic search across your codebase with sentence-transformers
- **Interactive visualization** — Collapsible, searchable HTML graph with edge-type toggles
- **Watch mode** — Real-time graph updates as you code

For the full feature list and changelog, see [docs/FEATURES.md](docs/FEATURES.md).

---

## 🚀 Quick Start

### Installation

```bash
pip install code-review-graph
```

Works on Python 3.10+. With semantic search (optional):

```bash
pip install code-review-graph[embeddings]
```

**Don't have Python 3.10+?** Use Docker instead:

```bash
docker run -v $(pwd):/repo tirth8205/code-review-graph build
```

### CLI

```bash
code-review-graph init       # Set up .mcp.json for Claude Code
code-review-graph build      # Parse your entire codebase
code-review-graph update     # Incremental update (only changed files)
code-review-graph watch      # Real-time auto-updates as you code
code-review-graph status     # Show graph statistics
code-review-graph visualize  # Interactive HTML graph visualization
code-review-graph serve      # Start MCP server
```

No git clone. No manual venv. No Python upgrade needed.

### Connect to Claude Code

```bash
code-review-graph init
```

This creates `.mcp.json` with the correct Python path. Restart Claude Code to pick up the new MCP server.

### Use the skills

```
/code-review-graph:build-graph    # Parse your codebase (~10s for 500 files)
/code-review-graph:review-delta   # Review only what changed
/code-review-graph:review-pr      # Full PR review with blast-radius
```

**Before**: Claude reads 200 files, uses ~150k tokens.
**After**: Claude reads 8 changed + 12 impacted files, uses ~25k tokens.

For detailed usage instructions, see [docs/USAGE.md](docs/USAGE.md).

---

## 🛠️ How It Works

```
┌─────────────────────────────────────────────┐
│                Claude Code                   │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐ │
│  │  Skills  │  │  Hooks   │  │   Agent    │ │
│  └────┬────┘  └────┬─────┘  └─────┬──────┘ │
│       │            │               │         │
│       └────────────┼───────────────┘         │
│                    │                         │
│              ┌─────▼─────┐                   │
│              │ MCP Server │                  │
│              └─────┬─────┘                   │
└────────────────────┼────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐  ┌──▼──────────┐
    │ Parser │  │ Graph  │  │ Incremental │
    │(sitter)│  │(SQLite)│  │  (git diff) │
    └────────┘  └────────┘  └─────────────┘
```

| Component | File | Role |
|-----------|------|------|
| **Parser** | `code_review_graph/parser.py` | Tree-sitter multi-language AST parser. Extracts nodes and relationships. |
| **Graph** | `code_review_graph/graph.py` | SQLite-backed knowledge graph with NetworkX for traversal queries. |
| **Incremental** | `code_review_graph/incremental.py` | Git-aware delta detection. Re-parses only changed files + dependents. |
| **MCP Server** | `code_review_graph/main.py` | Exposes 8 tools to Claude Code via the Model Context Protocol. |
| **Visualization** | `code_review_graph/visualization.py` | D3.js interactive graph visualization generator. |
| **Skills** | `skills/` | Three review workflows: `build-graph`, `review-delta`, `review-pr`. |
| **Hooks** | `hooks/` | Auto-updates the graph on file edits and git commits. |

For the full architecture walkthrough, see [docs/architecture.md](docs/architecture.md).

---

## 📚 Deep Dive

Everything beyond the quick start lives in the [docs/](docs/) folder. Start with [docs/USAGE.md](docs/USAGE.md) for the full workflow guide.

| Document | What's inside |
|----------|---------------|
| [Usage Guide](docs/USAGE.md) | Installation, workflows, and tips |
| [Commands Reference](docs/COMMANDS.md) | All MCP tools, skills, and CLI commands |
| [Features & Changelog](docs/FEATURES.md) | What's included and what changed |
| [Architecture](docs/architecture.md) | System design and data flow |
| [Schema](docs/schema.md) | Graph node/edge types and SQLite tables |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [LLM-Optimized Reference](docs/LLM-OPTIMIZED-REFERENCE.md) | Token-optimized reference used by Claude Code |
| [Roadmap](docs/ROADMAP.md) | Planned features |
| [Legal & Privacy](docs/LEGAL.md) | License and data handling |

---

## Graph Schema

### Nodes

| Kind | Properties |
|------|-----------|
| **File** | path, language, last_parsed_hash, size |
| **Class** | name, file, line_start, line_end, modifiers |
| **Function** | name, file, class (nullable), line_start, line_end, params, return_type, is_test |
| **Type** | name, file, kind (enum, interface, etc.) |
| **Test** | name, file, tested_function |

### Edges

| Kind | Direction | Meaning |
|------|-----------|---------|
| **CALLS** | Function -> Function | Function calls another function |
| **IMPORTS_FROM** | File -> File/Module | File imports from another |
| **INHERITS** | Class -> Class | Class extends another |
| **IMPLEMENTS** | Class -> Interface | Class implements an interface |
| **CONTAINS** | File/Class -> Function/Class | Containment hierarchy |
| **TESTED_BY** | Function -> Test | Function has a test |
| **DEPENDS_ON** | Node -> Node | General dependency |

For the full schema documentation, see [docs/schema.md](docs/schema.md).

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `build_or_update_graph_tool` | Full or incremental graph build |
| `get_impact_radius_tool` | Blast radius analysis for changed files |
| `query_graph_tool` | Predefined relationship queries (callers, callees, tests, imports) |
| `get_review_context_tool` | Token-optimized review context with source snippets |
| `semantic_search_nodes_tool` | Search code entities by name/keyword/semantic similarity |
| `embed_graph_tool` | Compute vector embeddings for semantic search |
| `list_graph_stats_tool` | Graph statistics and health check |
| `get_docs_section_tool` | Retrieve specific documentation sections (minimal tokens) |

For usage details and examples, see [docs/COMMANDS.md](docs/COMMANDS.md).

---

## Supported Languages

| Language | Extensions | Status |
|----------|-----------|--------|
| Python | `.py` | Full support |
| TypeScript | `.ts`, `.tsx` | Full support |
| JavaScript | `.js`, `.jsx` | Full support |
| Go | `.go` | Full support |
| Rust | `.rs` | Full support |
| Java | `.java` | Full support |
| C# | `.cs` | Full support |
| Ruby | `.rb` | Full support |
| Kotlin | `.kt` | Full support |
| Swift | `.swift` | Full support |
| PHP | `.php` | Full support |
| C/C++ | `.c`, `.h`, `.cpp`, `.hpp` | Full support |

---

## Configuration

Create a `.code-review-graphignore` file in your repo root to exclude paths:

```
# Ignore generated files
generated/**
*.generated.ts
*.pb.go

# Ignore vendor
vendor/**
third_party/**
```

---

## 🧪 Testing

```bash
pip install -e ".[dev]"
pytest
ruff check code_review_graph/
```

47 tests covering parser, graph storage, MCP tools, and multi-language support (Go, Rust, Java).

---

## 🤝 Contributing

### Adding a new language

1. Add the extension mapping in `code_review_graph/parser.py` → `EXTENSION_TO_LANGUAGE`
2. Add node type mappings in `_CLASS_TYPES`, `_FUNCTION_TYPES`, `_IMPORT_TYPES`, `_CALL_TYPES`
3. Test with a sample file in that language
4. Submit a PR

### Development setup

```bash
git clone https://github.com/tirth8205/code-review-graph.git
cd code-review-graph
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

---

## Comparison

| Feature | code-review-graph | code-graph-rag | CocoIndex |
|---------|:-:|:-:|:-:|
| Review-first design | Yes | No | No |
| Claude Code integration | Native | No | No |
| Incremental updates | Yes | Partial | Yes |
| No external DB needed | Yes (SQLite) | No (Neo4j) | No |
| Auto-update hooks | Yes | No | No |
| Impact/blast radius | Yes | No | No |
| Multi-language | 12+ languages | Python only | Varies |
| Token-efficient reviews | Yes | No | No |

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

<p align="center">Built with ❤️ for better code reviews</p>

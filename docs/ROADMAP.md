# Roadmap

## Shipped

### v1.5.0
- Generated files organized into `.code-review-graph/` directory (auto-gitignored, legacy migration)
- Visualization density: collapsed start, search, edge toggles, scale-aware layout
- Project cleanup: removed redundant files and directories

### v1.4.0
- `init` command for automatic `.mcp.json` setup
- Interactive D3.js graph visualization (`visualize` command)
- `serve` command to start MCP server directly
- Comprehensive documentation overhaul

### v1.3.0
- Python version check with Docker fallback
- Universal install via `pip install code-review-graph`
- CLI entry point (`code-review-graph` command)

### v1.2.0
- Logging improvements and watch debounce
- tools.py fixes and CI coverage via GitHub Actions

### v1.1.0
- Watch mode, vector embeddings, 12+ languages verified

## v1.5 (Planned)
- Auto-generated Mermaid diagrams in review output
- Public API change detection (breaking change warnings)
- Configurable review depth per-project
- Graph diff visualization (before/after a PR)

## v2.0 (Future)
- Surgical edit suggestions (auto-fix common patterns)
- GitHub PR bot integration
- Team sync (shared graph via git-tracked DB)
- Memgraph/Cypher support for large-scale graphs

## Ongoing
- Additional language grammars as requested
- Performance optimization for monorepos (>50k files)
- Integration with more Claude Code features as the platform evolves

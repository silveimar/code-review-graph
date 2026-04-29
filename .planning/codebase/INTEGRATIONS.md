# External Integrations

**Analysis Date:** 2026-04-29

## APIs & External Services

**AI/Embedding Providers:**
- OpenAI-compatible embeddings endpoint - semantic vector embedding provider
  - SDK/Client: internal HTTP client in `code_review_graph/embeddings.py` (`OpenAIEmbeddingProvider`)
  - Auth: `CRG_OPENAI_API_KEY` (+ `CRG_OPENAI_BASE_URL`, `CRG_OPENAI_MODEL`)
- Google Gemini embeddings - cloud embeddings provider
  - SDK/Client: `google-generativeai` optional dependency (`pyproject.toml`, `code_review_graph/embeddings.py`)
  - Auth: `GOOGLE_API_KEY`
- MiniMax embeddings API (`https://api.minimax.io/v1/embeddings`) - cloud embeddings provider
  - SDK/Client: direct `urllib.request` call in `code_review_graph/embeddings.py`
  - Auth: `MINIMAX_API_KEY`

**Developer Platform Integrations:**
- MCP client platforms (Codex, Claude Code, Cursor, Windsurf, Zed, Continue, OpenCode, Antigravity, Qwen, Kiro, Qoder) - auto-generated MCP config install targets in `code_review_graph/skills.py`
  - SDK/Client: local config writers in `code_review_graph/skills.py`
  - Auth: Not applicable (local config integration)

## Data Storage

**Databases:**
- SQLite (local file database) in `.code-review-graph/graph.db`
  - Connection: path resolution via `CRG_DATA_DIR` / repo root (`code_review_graph/incremental.py`)
  - Client: Python `sqlite3` in `code_review_graph/graph.py`; `better-sqlite3` in `code-review-graph-vscode/src/backend/sqlite.ts`

**File Storage:**
- Local filesystem only (graph DB, generated wiki/output files, registry JSON) in `code_review_graph/incremental.py`, `code_review_graph/registry.py`, `code_review_graph/wiki.py`

**Caching:**
- In-process cache only (e.g., NetworkX graph cache and connection pool) in `code_review_graph/graph.py`, `code_review_graph/registry.py`

## Authentication & Identity

**Auth Provider:**
- Custom token/env-var based API auth for cloud embedding providers
  - Implementation: environment-variable key injection inside provider clients in `code_review_graph/embeddings.py`

## Monitoring & Observability

**Error Tracking:**
- None (no external SaaS error tracker detected in repo config/workflows)

**Logs:**
- Standard Python logging throughout core modules (`code_review_graph/*.py`)
- GitHub Actions logs for CI and release workflows (`.github/workflows/ci.yml`, `.github/workflows/publish.yml`)

## CI/CD & Deployment

**Hosting:**
- Package distribution to PyPI (`.github/workflows/publish.yml`)
- Runtime hosting model is user-local CLI/MCP server (stdio or streamable HTTP) via `code_review_graph/cli.py`

**CI Pipeline:**
- GitHub Actions with lint, type-check, security scan, schema sync, and test matrix in `.github/workflows/ci.yml`

## Environment Configuration

**Required env vars:**
- Core runtime/config: `CRG_REPO_ROOT`, `CRG_DATA_DIR`, `CRG_GIT_TIMEOUT`, `CRG_RECURSE_SUBMODULES`, `CRG_TOOLS`
- Limits/tuning: `CRG_MAX_IMPACT_NODES`, `CRG_MAX_IMPACT_DEPTH`, `CRG_MAX_BFS_DEPTH`, `CRG_MAX_SEARCH_RESULTS`, `CRG_DEPENDENT_HOPS`, `CRG_PARSE_WORKERS`, `CRG_SERIAL_PARSE`
- Embeddings: `CRG_EMBEDDING_MODEL`, `CRG_OPENAI_API_KEY`, `CRG_OPENAI_BASE_URL`, `CRG_OPENAI_MODEL`, `CRG_OPENAI_DIMENSION`, `CRG_OPENAI_BATCH_SIZE`, `MINIMAX_API_KEY`, `GOOGLE_API_KEY`, `CRG_ACCEPT_CLOUD_EMBEDDINGS`
- Release: `PYPI_API_TOKEN` (GitHub Actions secret used as `TWINE_PASSWORD`) in `.github/workflows/publish.yml`

**Secrets location:**
- Process environment variables and GitHub Actions secrets (`.github/workflows/publish.yml`)
- No checked-in `.env` file detected at repo root

## Webhooks & Callbacks

**Incoming:**
- None detected (no webhook endpoint service in repository runtime)

**Outgoing:**
- Outbound HTTP to cloud embedding APIs when non-local providers are selected (`code_review_graph/embeddings.py`)
- Outbound upload to PyPI during release job (`.github/workflows/publish.yml`)

---

*Integration audit: 2026-04-29*

# Codebase Concerns

**Analysis Date:** 2026-04-29

## Tech Debt

**[P1] Duplicate source and test files committed as numbered copies:**
- Issue: Multiple Python modules and tests exist as duplicate copies with suffixed names (`" 2.py"`, `" 3.py"`), creating parallel edit surfaces.
- Files: `code_review_graph/analysis.py`, `code_review_graph/analysis 2.py`, `code_review_graph/enrich.py`, `code_review_graph/enrich 2.py`, `code_review_graph/enrich 3.py`, `code_review_graph/exports.py`, `code_review_graph/exports 2.py`, `code_review_graph/exports 3.py`, `code_review_graph/jedi_resolver.py`, `code_review_graph/jedi_resolver 2.py`, `tests/test_cli.py`, `tests/test_cli 2.py`, `tests/test_enrich.py`, `tests/test_enrich 2.py`, `tests/test_postprocessing.py`, `tests/test_postprocessing 2.py`
- Impact: Bug fixes can land in one copy and miss others; reviewers and future agents can modify dead copies; packaging and maintenance complexity increase.
- Fix approach: Remove redundant copies and keep a single canonical module/test per concern area; add CI guard that fails on filename pattern `* [0-9].py`.

**[P2] Monolithic modules increase change risk and review cost:**
- Issue: Core modules are very large and hold multiple responsibilities.
- Files: `code_review_graph/parser.py` (~4750 LOC), `code_review_graph/visualization.py` (~1952 LOC), `code_review_graph/graph.py` (~1358 LOC), `code_review_graph/incremental.py` (~1103 LOC), `code_review_graph/skills.py` (~1088 LOC), `code_review_graph/main.py` (~998 LOC), `code_review_graph/cli.py` (~988 LOC)
- Impact: Higher regression probability for small edits, slower onboarding, and harder targeted testing.
- Fix approach: Split by bounded responsibilities (e.g., parser language handlers, CLI command groups, graph query/read-write separation) with compatibility-preserving facades.

## Known Bugs

**[P2] Silent filesystem/config failures in daemon state paths:**
- Symptoms: State/config cleanup errors are swallowed without actionable detail.
- Files: `code_review_graph/daemon.py` (silent `pass` on `OSError` in config polling and state cleanup paths)
- Trigger: Transient permission or filesystem errors while watcher state/config is updated.
- Workaround: Inspect daemon logs and manually verify daemon state files.

## Security Considerations

**[P2] Broad exception swallowing in runtime-critical paths reduces security observability:**
- Risk: Unexpected parsing/indexing/runtime failures can be downgraded to warnings or suppressed, making malicious or malformed input behavior harder to detect quickly.
- Files: `code_review_graph/incremental.py` (`except Exception` in parse/update loops), `code_review_graph/daemon.py` (`except Exception` around process start/health paths), `code_review_graph/search.py` (fallbacks on broad exceptions), `code_review_graph/graph.py` (FTS failure silently ignored)
- Current mitigation: Several warnings are logged and some security checks are documented in `pyproject.toml` and project docs.
- Recommendations: Replace broad catches with scoped exception classes where feasible; keep fallback behavior but emit structured warning context (file/path/operation/error class).

## Performance Bottlenecks

**[P1] Parse pipeline is CPU-heavy and single-writer constrained:**
- Problem: Parsing is parallelized, but graph writes are serialized through one SQLite writer.
- Files: `code_review_graph/incremental.py` (parallel `ProcessPoolExecutor` parse + serial `store.store_file_nodes_edges(...)`)
- Cause: Process pool fan-out plus single-writer persistence can shift bottleneck to DB write stage on large repos.
- Improvement path: Batch writes in transactions per chunk, profile parse-vs-write time ratios, and tune worker/chunk strategy with measured thresholds.

**[P2] Heavy fallback paths in search can degrade latency:**
- Problem: Search may fall back from FTS/embedding to `LIKE` scans.
- Files: `code_review_graph/search.py`, `code_review_graph/graph.py`
- Cause: On FTS unavailability or embedding failure, broader SQL matching performs less efficiently.
- Improvement path: Ensure FTS initialization invariants at startup and expose health diagnostics to avoid frequent runtime fallback.

## Fragile Areas

**[P1] Daemon process lifecycle management has multiple soft-failure paths:**
- Files: `code_review_graph/daemon.py`, `code_review_graph/daemon_cli.py`
- Why fragile: Child-process orchestration relies on polling, file state, and broad exception handling; failure branches often continue execution.
- Safe modification: Add focused unit tests before changing lifecycle logic; prefer explicit failure surfaces over silent continuation.
- Test coverage: `tests/test_daemon.py` exists, but duplicate test files in repository indicate maintenance drift risk.

**[P2] Cross-language parser surface is difficult to change safely:**
- Files: `code_review_graph/parser.py`, `tests/test_multilang.py`, `tests/test_notebook.py`
- Why fragile: One module handles many language grammars and notebook parsing modes, increasing coupling.
- Safe modification: Isolate per-language extractors behind stable interfaces and add language-specific regression tests for touched paths.
- Test coverage: Broad parser tests exist, but module size indicates high probability of hidden coupling.

## Scaling Limits

**[P2] Large-repo scaling tied to local CPU + SQLite write throughput:**
- Current capacity: Worker count is capped by `CRG_PARSE_WORKERS` defaulting to `min(cpu_count, 8)` in `code_review_graph/incremental.py`.
- Limit: For very large repositories, parsing throughput and serialized persistence can become the dominant wall-clock limit.
- Scaling path: Add measured adaptive worker tuning and persistence batching; expose timings in build/update output for operational tuning.

## Dependencies at Risk

**[P3] Optional integrations create behavior variance across environments:**
- Risk: Feature behavior differs when optional providers/tools are absent or partially configured.
- Impact: Search and embeddings behavior may silently degrade to fallback modes.
- Migration plan: Add startup diagnostics that report capability matrix (FTS, embeddings providers, optional extras) and hard-fail only for explicitly requested features.

## Missing Critical Features

**[P2] Missing automated repository hygiene checks for duplicate files:**
- Problem: No guardrail prevents duplicate numbered files from reappearing.
- Blocks: Reliable maintainability and confident refactoring in core modules.

## Test Coverage Gaps

**[P1] No test guard for duplicate source/test artifacts:**
- What's not tested: Repository-level invariant that canonical modules/tests are unique.
- Files: `tests/` (no test enforcing duplicate-file prohibition), duplicated artifacts under `code_review_graph/` and `tests/`
- Risk: Regression and confusion can be reintroduced unnoticed.
- Priority: High

**[P2] Limited direct assertions on fallback observability and error classification:**
- What's not tested: Consistency/quality of logged error metadata for broad exception fallback paths.
- Files: `code_review_graph/incremental.py`, `code_review_graph/daemon.py`, `code_review_graph/search.py`
- Risk: Operational debugging slows during production incidents.
- Priority: Medium

---

*Concerns audit: 2026-04-29*

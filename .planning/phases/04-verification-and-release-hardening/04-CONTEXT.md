# Phase 4: Verification and Release Hardening - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Prove and ship the **full local-only security posture**: an **end-to-end hardening verification suite**, **CI regression coverage** so controls do not rot, and **release-grade checklist/documentation** so operators can confirm readiness (REQ-01–REQ-07 as summarized in ROADMAP Phase 4). This phase is **verification and packaging**, not new security mechanisms — Phases 1–3 own the controls.

</domain>

<decisions>
## Implementation Decisions

### E2E hardening suite shape

- **D-01:** **Hybrid orchestration** — keep a **thin E2E layer** (orchestration module) that **reuses helpers and patterns** from existing security tests (`test_policy_verify`, `test_egress_guard`, `test_retention_*`, artifact/encryption tests, etc.) rather than duplicating assertions or splitting logic inconsistently.

- **D-02:** **Execution surface:** **Both** — use **subprocess** for **critical realism** (e.g. `verify-policy`, destructive-safe CLI paths) and **in-process** calls for **bulk/fast assertions** and shared fixtures.

- **D-03:** **MCP / server coverage:** **Claude's discretion** — include **minimal or broader MCP smoke** only where planning shows a **gap** vs existing MCP/tool tests; do not mandate depth by default.

- **D-04:** **Fixture breadth:** **Claude's discretion** — **start minimal** (one solid temp-repo path), **add scenarios** when verification finds gaps (optional embeddings path, registry vs repo dot-dir, etc.).

### CI security regressions

User **skipped interactive prompts** for this subsection — **planning defaults** below apply until revised.

- **D-05:** **Placement:** Integrate hardening/E2E tests into the **existing pytest suite** and **`test` CI job + Python matrix** (same pattern as `tests/test_*` today — see `.planning/codebase/TESTING.md`). Add a **separate CI job** only if research shows isolation needs (dependencies, timeouts, or different failure semantics).

- **D-06:** **Merge gate:** **No weaker gate than today** — **all CI jobs green** on PRs to `main`, including **full pytest matrix with coverage floor**, unless a future split is justified by runtime evidence and documented.

### Release checklist and operator proof

Skipped prompts — defaults tied to **REQUIREMENTS** and **ROADMAP** success criteria.

- **D-07:** **Artifacts:** Deliver **both** — **operator-facing markdown** in `docs/` (runbook/checklist style, links to commands) **and** **machine-checkable** steps where REQ-07 implies proof (`verify-policy` / CLI aggregates), so CI and humans can align.

- **D-08:** **Release readiness bar:** **Automated validation first** — hardening suite + policy verification paths **pass in CI** on `main`; **documented manual spot-checks** only where automation cannot reasonably cover (e.g. platform-specific permission nuances called out in docs). **Formal sign-off blocks** beyond maintainer review are **not** required unless you revise this context later.

### Python matrix vs CI cost

Skipped prompts — planning default:

- **D-09:** **Default:** Run **hardening/E2E tests on the **full Python matrix** (3.10–3.13) to match **determinism/reliability** expectations in REQUIREMENTS. **If** runtime becomes prohibitive, introduce **`@pytest.mark`** or job splitting so **full orchestration runs on one version** and **smoke subset** runs on others — **research/planner** proposes based on measured CI time.

### Claude's Discretion

- Exact **file names** for orchestration (`tests/test_hardening_e2e.py` vs package), **pytest markers**, and **subprocess command list**.
- **CI job split** only if justified.
- **MCP smoke** inclusion and **fixture count** beyond D-03/D-04.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/REQUIREMENTS.md` — REQ-01 through REQ-07; acceptance criteria for verification and CI.
- `.planning/ROADMAP.md` — Phase 4 goal, success criteria, plan titles 04-01–04-03.
- `.planning/PROJECT.md` — local-only vision, constraints, success metrics.

### Prior phase context

- `.planning/phases/03-retention-deletion-and-operational-safety/03-CONTEXT.md` — retention/cleanup decisions; E2E suite explicitly deferred to Phase 4.
- `.planning/phases/02-data-protection-and-access-controls/02-CONTEXT.md` — encryption scope and fail-closed behavior for artifact paths.

### Testing and CI

- `.planning/codebase/TESTING.md` — pytest layout, coverage expectations, integration vs E2E patterns.
- `.github/workflows/ci.yml` — lint, mypy, bandit, schema-sync, pytest matrix, coverage threshold.

### Implementation anchors

- `code_review_graph/cli.py` — CLI entrypoints for verify/cleanup/policy flows.
- `tests/test_policy_verify.py`, `tests/test_egress_guard.py`, `tests/test_retention_cleanup.py`, `tests/test_artifact_encryption.py` — existing security regression surfaces to compose from.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **Pytest suites** under `tests/` — class/setup patterns, temp DB/files, `monkeypatch` for env (`TESTING.md`).
- **CI** — bandit already in `security` job; full matrix in `test` job.
- **Security modules** — policy loader, audit, retention eval, artifact crypto — orchestration should call these paths intentionally rather than re-specifying behavior.

### Established patterns

- **No browser E2E** — library/CLI/server testing scope per `TESTING.md`; “E2E” here means **cross-module posture verification**, not Selenium.

### Integration points

- **`verify-policy` and related CLI** — natural subprocess anchors for release proof (REQ-07).
- **GitHub Actions** — extend existing jobs before adding parallel complexity.

</code_context>

<specifics>
## Specific Ideas

- User selected **all four** gray areas (E2E, CI, release, matrix). **E2E** choices captured interactively; **CI / release / matrix** used **planning defaults** after prompts were skipped.

</specifics>

<deferred>
## Deferred Ideas

- **Hosted/SaaS verification** — out of scope per `PROJECT.md`.
- **Encrypting `~/.code-review-graph` registry** — optional follow-up if low-cost; not locked here.

### Reviewed Todos (not folded)

_None — no matching todos from tracker._

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-verification-and-release-hardening*
*Context gathered: 2026-04-29*

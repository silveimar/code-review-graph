# Phase 3: Retention, Deletion, and Operational Safety - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Add **lifecycle controls** so residual sensitive analysis data under `.code-review-graph/` can be bounded and removed deliberately: configurable retention, secure-enough deletion workflows for local threat models, and **runbook-grade** operator guidance (REQ-05, REQ-06). Discussion clarifies policy shape and surfaces — not Phase 4 release gates.

</domain>

<decisions>
## Implementation Decisions

### Retention policy model (REQ-05)

- **D-01:** **Time-based limits per artifact category are primary** (e.g. audit traces vs memory vs wiki outputs vs graph DB). Optional size caps may appear in plans as secondary guards where time alone is insufficient.

### Enforcement / when cleanup runs

- **D-02:** **Claude's discretion:** Prefer **explicit operator-driven cleanup** with **dry-run** and clear previews before destructive work. Optional integration with `build`/`update` or hardened-local hints is allowed in plans only if it remains **opt-in** or confirmation-gated — no silent automatic purge as the default.

### Secure deletion semantics

- **D-03:** **Pragmatic local deletion:** Use normal file unlink / SQLite row deletion and **VACUUM** or equivalent where applicable; **document residual risks** (e.g. SSD wear-leveling, plaintext when encryption off). Do **not** claim military-grade wipe; align honesty with REQ-05.

### Operator UX & verification

- **D-04:** **Claude's discretion:** Stay consistent with existing CLI patterns (`code_review_graph/cli.py`). Recommended direction: **extend policy/verification reporting** for “what would be removed” and **separate explicit cleanup actions** so audits and destructive operations are not conflated — exact command names and flags are for planning/research.

### Claude's Discretion

- Default retention horizons per category (until research cites operational reality).
- Whether SQLite/SQLCipher paths need special handling beyond D-03.
- Runbook location (`docs/` vs generated wiki) and overlap with `verify-policy` JSON blocks.

</decisions>

<specifics>
## Specific Ideas

- User chose **all gray areas** in discuss; **time-primary retention** and **pragmatic deletion + documented residuals** are explicit locks; enforcement and operator surfaces delegated with guardrails above.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/REQUIREMENTS.md` — REQ-05 (retention and secure deletion), REQ-06 (audit traces for security-relevant actions).
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, plan placeholders.
- `.planning/PROJECT.md` — local-only vision and constraints.

### Prior phase

- `.planning/phases/02-data-protection-and-access-controls/02-CONTEXT.md` — artifact boundaries under `.code-review-graph/`, encryption fail-closed behavior.
- `.planning/phases/01-policy-foundation-and-threat-boundaries/01-CONTEXT.md` — policy profile / hardened_local machinery (if referenced by plans).

### Codebase maps

- `.planning/codebase/ARCHITECTURE.md` — CLI vs MCP entry surfaces and data plane.
- `.planning/codebase/CONCERNS.md` — known gaps relevant to filesystem and tooling.

### Implementation anchors (from scout)

- `code_review_graph/cli.py` — command routing for new retention/cleanup surfaces.
- `code_review_graph/incremental.py` — existing purge/stale handling patterns.
- `code_review_graph/memory.py` — memory tree deletion helpers.
- `code_review_graph/graph.py` — SQLite lifecycle.
- `code_review_graph/security/` — policy loading and audit emission for cleanup-related events.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable assets

- **GraphStore** — centralized DB path and transactions for retention inside SQLite.
- **Policy / audit** — extend audit events for deletion and retention evaluation where REQ-06 applies.
- **Incremental pipeline** — prior art for “purge stale” logic when sources disappear.

### Established patterns

- Repo-local `.code-review-graph/` as canonical tree; multi-repo registry paths may be out of scope unless plans explicitly include them.

### Integration points

- New retention evaluation likely connects to policy loader from Phase 1 and artifact writers from Phase 2.

</code_context>

<deferred>
## Deferred Ideas

- Phase 4 end-to-end verification suite — stays in Phase 4 per roadmap.
- Cloud or remote artifact retention — out of scope per PROJECT.md.

</deferred>

---

*Phase: 03-retention-deletion-and-operational-safety*
*Context gathered: 2026-04-29*

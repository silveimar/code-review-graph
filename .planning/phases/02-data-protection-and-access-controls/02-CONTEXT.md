# Phase 2: Data Protection and Access Controls - Context

**Gathered:** 2026-04-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver documented and enforced protection for **local persisted artifacts**: SQLite graph data, audit traces, memory artifacts, and wiki outputs under the repository `.code-review-graph/` tree (and any aligned paths), plus strict filesystem-oriented access controls consistent with REQ-03, REQ-04, and REQ-06.

Scope is **how** to implement artifact protection and access checks — not new product features outside the roadmap phase.

</domain>

<decisions>
## Implementation Decisions

### Artifact encryption (REQ-03)

- **D-01:** **Hybrid protection model.** Baseline for all users is **documented full-disk encryption (FDE) expectations** plus **filesystem permission hardening** for `.code-review-graph/`. In **`hardened_local`**, the product additionally supports **optional application-layer encryption** gated by policy and environment configuration (Phase 1 security profile/policy machinery applies).

- **D-02:** When application-layer encryption is **enabled** for `hardened_local`, the encryption scope **must cover all sensitive artifacts under the repo dot-directory**, including at minimum: **`graph.db`**, **policy audit JSONL** (and any successor audit sinks under `.code-review-graph/`), **`memory/`** tree, and **`wiki/`** generated outputs — aligned with current module paths (`code_review_graph/graph.py`, `code_review_graph/security/audit.py`, `code_review_graph/memory.py`, wiki tooling).

- **D-03:** **Fail-closed key policy.** If `hardened_local` policy requires encryption **but key material is not configured**, the runtime **must refuse** to perform protected reads/writes that would expose or persist plaintext sensitive artifacts — **no silent fallback** to unencrypted operation for those artifacts.

### Permission and access control (REQ-04)

- **D-04:** **Claude's discretion:** Specific creation masks, verification CLI surfaces, and cross-platform permission checks are left to research/planning, constrained by D-01–D-03 and existing `_validate_repo_root` / path-safety patterns in `code_review_graph/tools/_common.py`.

### Audit expansion (REQ-06)

- **D-05:** **Claude's discretion:** Which additional operations beyond Phase 1 policy events emit audit records will be specified in plans; this discussion locked encryption scope and failure mode only.

### Claude's Discretion

- Exact **environment variable names** and optional **key derivation** design for application-layer encryption (must satisfy D-03 and integrate with Phase 1 policy schema).
- Whether encryption uses **file-level envelope**, **SQLCipher-style DB encryption**, or **directory quotas** — as long as D-02 coverage and fail-closed behavior are met.
- Incremental rollout across writers (graph vs wiki vs memory) **ordering** within Phase 2 plans.

### Folded Todos

_None._

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/REQUIREMENTS.md` — REQ-03, REQ-04, REQ-06 definitions.
- `.planning/ROADMAP.md` — Phase 2 goal, dependencies, success criteria.
- `.planning/PROJECT.md` — local-only hardening vision and constraints.

### Prior phase and research

- `.planning/research/LOCAL_SECURITY_FOUNDATIONS.md` — data-at-rest and access-control research baseline.
- `.planning/phases/01-policy-foundation-and-threat-boundaries/01-VERIFICATION.md` — verified Phase 1 policy/audit/verify behaviors to build upon.

### Implementation anchors

- `code_review_graph/graph.py` — graph persistence (`GraphStore`, SQLite paths).
- `code_review_graph/security/audit.py` — structured local audit sink defaults under `.code-review-graph/`.
- `code_review_graph/memory.py` — memory artifact directory layout.
- `code_review_graph/tools/_common.py` — repo_root validation and `.code-review-graph` boundary expectations.
- `.planning/codebase/ARCHITECTURE.md` — data plane and entry surfaces.
- `.planning/codebase/CONCERNS.md` — known filesystem/daemon observability gaps relevant to enforcement.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **Phase 1 security modules** (`code_review_graph/security/`) — policy profiles, audit emitter, egress guard; Phase 2 encryption gates should reuse policy loading and hardened_local semantics.
- **`GraphStore`** — centralized SQLite access for `.code-review-graph/graph.db`.
- **Audit JSONL** — append-only policy audit path convention under `.code-review-graph/`.

### Established Patterns

- Repo-relative `.code-review-graph/` as the canonical artifact root; registry multi-repo uses `~/.code-review-graph/` separately — encryption decisions for Phase 2 focus on **repo dot-dir** per discussion; registry may be a follow-up if plans warrant.

### Integration Points

- Graph open/write paths, audit writes, memory persistence, wiki/doc generators — any code creating files under `.code-review-graph/` must respect D-01–D-03 once encryption is enabled.

</code_context>

<specifics>
## Specific Ideas

- User selected discussion focus **artifact encryption scope** only; hybrid model with **full sensitive-dot-dir coverage** and **fail-closed** behavior when keys are missing under hardened_local.

</specifics>

<deferred>
## Deferred Ideas

- **Retention / secure deletion** — REQ-05 remains Phase 3 per roadmap; do not implement lifecycle deletion here unless plans explicitly extend scope.
- **Enterprise IAM** — out of scope per PROJECT.md.
- **Encrypting `~/.code-review-graph` registry** — not locked in this discussion; note for planner if low-cost alignment is possible.

### Reviewed Todos (not folded)

_None._

None — discussion stayed within phase scope for selected areas.

</deferred>

---

*Phase: 2-data-protection-and-access-controls*
*Context gathered: 2026-04-29*

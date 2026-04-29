# Phase 2: Data Protection and Access Controls - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 2-data-protection-and-access-controls
**Areas discussed:** Artifact encryption scope

---

## Gray area selection

**Question:** Which areas to discuss?

| Option | Selected |
|--------|----------|
| Artifact encryption scope | ✓ |
| Filesystem permission defaults | |
| Sensitive-operation audit scope | |
| Key material (app-layer crypto) | |

---

## Artifact encryption scope

| Option | Description | Selected |
|--------|-------------|----------|
| Documented FDE + permissions | No new in-app encryption; OS FDE + lock down `.code-review-graph/` perms | |
| App-layer graph encryption | Encrypt `graph.db` in hardened mode; may add crypto deps | |
| Hybrid | FDE + permissions baseline; optional env-gated encryption for sensitive artifacts in hardened_local | ✓ |

**User's choice:** Hybrid model.

**Follow-up — encrypted surface when app-layer encryption is on:**

| Option | Selected |
|--------|----------|
| graph.db only | |
| graph.db + policy audit JSONL | |
| All sensitive dot-dir artifacts (graph, audit, memory, wiki) | ✓ |

**Follow-up — behavior if encryption required but key missing:**

| Option | Selected |
|--------|----------|
| Fail closed | ✓ |
| Degrade with warning / non-zero verify | |

**Notes:** User constrained Phase 2 encryption scope to comprehensive coverage under `.code-review-graph/` when encryption is enabled, with strict failure when keys are absent.

---

## Claude's Discretion

- Exact env var names and crypto mechanisms — see CONTEXT.md.

## Deferred Ideas

- Registry path `~/.code-review-graph/` encryption alignment — noted in CONTEXT deferred section.

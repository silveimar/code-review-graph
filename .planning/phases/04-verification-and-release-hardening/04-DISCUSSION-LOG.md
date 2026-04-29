# Phase 4: Verification and Release Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-29
**Phase:** 4 — Verification and Release Hardening
**Areas discussed:** E2E hardening suite shape, CI security regressions (defaults), Release checklist (defaults), Python matrix (defaults)

---

## E2E hardening suite shape

| Option | Description | Selected |
|--------|-------------|----------|
| Dedicated module(s) | Obvious release gate file layout | |
| Extend existing files only | Minimal new files | |
| Hybrid orchestration | Thin layer + reuse existing tests | ✓ |
| You decide | Planner picks structure | |

| Option | Description | Selected |
|--------|-------------|----------|
| In-process only | Fast, direct Python | |
| Subprocess CLI | Real shell commands | |
| Both | Subprocess for critical paths; in-process for bulk | ✓ |
| You decide | Balance speed vs fidelity | |

| Option | Description | Selected |
|--------|-------------|----------|
| CLI + library only | No MCP in Phase 4 suite | |
| Minimal MCP smoke | Short-lived server check | |
| Broader MCP coverage | Multiple tools | |
| You decide | Include MCP only if gap found | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| One golden temp repo | Simplest maintenance | |
| Few scenarios | Minimal + one variant | |
| Several scenarios | Broad coverage | |
| You decide | Start minimal, extend if gaps | ✓ |

**User's choice:** Hybrid orchestration; subprocess + in-process; MCP and fixture count delegated with discretion as documented in CONTEXT.md.

**Notes:** User advanced to next area after E2E; no extra E2E rounds.

---

## CI security regressions

Interactive questions were **skipped** in-session. **Planning defaults** recorded in CONTEXT.md (integrate with existing `test` job/matrix; no weaker merge gate).

---

## Release checklist and operator proof

Interactive questions were **skipped** in-session. Defaults: docs + scripted checks where REQ-07 applies; readiness anchored on CI green plus documented manual gaps only where needed.

---

## Python matrix vs CI cost

Interactive questions were **skipped** in-session. Default: full matrix unless CI time forces marker-based split.

---

## Claude's Discretion

- MCP depth and extra fixtures (E2E).
- CI job split if isolation needed.
- Pytest markers / orchestration filenames.

## Deferred Ideas

- Hosted verification — out of scope.
- Registry encryption hardening — optional future work.

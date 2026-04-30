# Project: Local-Only Secure Code Review Graph

## Current state (v1.0 shipped)

**2026-04-30:** Milestone **v1.0 — Local-Only Security Hardening** is complete. The codebase delivers a selectable **hardened_local** profile with centralized egress enforcement, optional encryption and filesystem permission controls, retention and secure deletion, local audit traces, and documented verification paths (`verify-policy`, operator checklists, CI-aligned pytest including `hardening_posture`). Formal verification artifacts live under `.planning/phases/` (`03-VERIFICATION.md`, `04-VERIFICATION.md`). See `.planning/MILESTONES.md` and `.planning/milestones/v1.0-*.md`.

## Vision

Strengthen this project for local-only use so analyzed code/content stays protected on-device, with explicit security controls, verifiable handling, and minimal data exposure risk.

## Problem (historical framing)

The system was powerful, but local deployment hardening and privacy guarantees were not captured as a first-class contract — **addressed in v1.0**.

## Outcome (achieved in v1.0)

A hardened local profile that:

- avoids sending repository content to external services by default,
- protects local artifacts at rest and in runtime,
- provides auditability and retention controls,
- keeps developer UX practical for day-to-day review workflows.

## In scope (v1.0)

- Local-only execution mode and policy enforcement.
- Data-at-rest protection for graph DB and generated artifacts.
- Access control, logging, and tamper-aware auditing.
- Retention and secure deletion lifecycle.
- Documentation, verification steps, and operational guidance.

## Out of scope

- Hosted SaaS mode for protected repositories.
- Multi-tenant remote service architecture.
- Enterprise IAM integrations beyond local role/profile patterns.

## Constraints

- Must remain usable for solo and small-team local workflows.
- Security controls should be on by default in hardened mode.
- Changes must not require cloud services for core functionality.

## Success metrics (v1.0)

- No analyzed source/content leaves machine in hardened mode (policy + egress enforcement).
- Security profile enabled with deterministic config (`hardened_local`).
- Test coverage includes privacy and enforcement pathways (including orchestrated posture tests).
- Operational docs provide reproducible verification steps.

## Next milestone goals

To be defined via `/gsd-new-milestone`. Candidate themes might include multi-repo operator ergonomics, expanded CI gates, or product features outside the v1.0 hardening charter — **not decided here**.

## Key decisions (v1.0 snapshot)

| Decision | Outcome |
|----------|---------|
| Centralized egress guard | All outbound-capable paths consult `check_egress` |
| Fail-closed policy load | Invalid/missing policy surfaces errors and audit |
| Retention / cleanup | Dry-run default; `--apply` for destructive work |
| Formal GSD verification | `03-VERIFICATION.md` / `04-VERIFICATION.md` for milestone REQ trace |

---

*Last updated: 2026-04-30 after v1.0 milestone archive*

# Project: Local-Only Secure Code Review Graph

## Vision
Strengthen this project for local-only use so analyzed code/content stays protected on-device, with explicit security controls, verifiable handling, and minimal data exposure risk.

## Problem
The current system is powerful, but local deployment hardening and privacy guarantees are not yet captured as a first-class project contract.

## Outcome
Deliver a hardened local profile that:
- avoids sending repository content to external services by default,
- protects local artifacts at rest and in runtime,
- provides auditability and retention controls,
- keeps developer UX practical for day-to-day review workflows.

## In Scope
- Local-only execution mode and policy enforcement.
- Data-at-rest protection for graph DB and generated artifacts.
- Access control, logging, and tamper-aware auditing.
- Retention and secure deletion lifecycle.
- Documentation, verification steps, and operational guidance.

## Out of Scope
- Hosted SaaS mode for protected repositories.
- Multi-tenant remote service architecture.
- Enterprise IAM integrations beyond local role/profile patterns.

## Constraints
- Must remain usable for solo and small-team local workflows.
- Security controls should be on by default in hardened mode.
- Changes must not require cloud services for core functionality.

## Success Metrics
- No analyzed source/content leaves machine in hardened mode.
- Security profile can be enabled with deterministic config.
- Test coverage includes privacy and enforcement pathways.
- Operational docs provide reproducible verification steps.

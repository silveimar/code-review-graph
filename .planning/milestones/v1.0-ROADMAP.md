# Roadmap: Local-Only Security Hardening

## Overview

Deliver a hardening-first progression that establishes local policy enforcement first, then data protection and lifecycle controls, and finally release-grade verification.

## Phases

- [x] **Phase 1: Policy Foundation and Threat Boundaries** - Define centralized local-only policy enforcement.
- [x] **Phase 2: Data Protection and Access Controls** - Protect local artifacts and runtime access.
- [x] **Phase 3: Retention, Deletion, and Operational Safety** - Add lifecycle controls and cleanup guarantees.
- [x] **Phase 4: Verification and Release Hardening** - Validate and ship hardened-local profile safely.
- [x] **Phase 5: Retention Phase Formal Verification** - Publish `03-VERIFICATION.md` to close milestone traceability for REQ-05/REQ-06.
- [x] **Phase 6: Release Phase Formal Verification** - Publish `04-VERIFICATION.md` to close milestone traceability for Phase 4 requirement rows.

## Phase Details

### Phase 1: Policy Foundation and Threat Boundaries
**Goal**: Define and implement centralized local-only policy enforcement.
**Depends on**: Nothing (first phase)
**Requirements**: [REQ-01, REQ-02, REQ-06, REQ-07]
**Success Criteria** (what must be TRUE):
  1. Hardened local profile exists and is selectable.
  2. Egress guard fails closed for protected content paths.
  3. Operators can verify local-only policy status via command/output.
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Add hardened-local configuration profile and policy schema
- [x] 01-02-PLAN.md — Implement centralized egress guard for outbound integrations
- [x] 01-03-PLAN.md — Add local policy verification report and audit baseline

### Phase 2: Data Protection and Access Controls
**Goal**: Protect local artifacts and restrict unauthorized local access.
**Depends on**: Phase 1
**Requirements**: [REQ-03, REQ-04, REQ-06]
**Success Criteria** (what must be TRUE):
  1. Local artifacts use documented encryption/protection strategy.
  2. Access control checks enforce secure file/runtime permissions.
  3. Audit events are emitted for sensitive operations.
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Artifact encryption policy, crypto module, graph/audit/memory/wiki integration (REQ-03)
- [x] 02-02-PLAN.md — Filesystem permissions for `.code-review-graph/` and verify-policy reporting (REQ-04)
- [x] 02-03-PLAN.md — Audit expansion for encryption and permission events (REQ-06)

### Phase 3: Retention, Deletion, and Operational Safety
**Goal**: Add lifecycle controls to minimize residual sensitive data.
**Depends on**: Phase 2
**Requirements**: [REQ-05, REQ-06]
**Success Criteria** (what must be TRUE):
  1. Retention policies can be configured and enforced.
  2. Secure deletion/cleanup workflows remove target artifacts.
  3. Operators have runbook-grade guidance for cleanup verification.
**Plans**: 3 plans

Plans:
- [x] 03-01: Add retention policy model and enforcement entry points
- [x] 03-02: Implement secure deletion and cleanup commands
- [x] 03-03: Publish operational safety runbook and checks

### Phase 4: Verification and Release Hardening
**Goal**: Validate full local-only security posture and ship safely.
**Depends on**: Phase 3
**Requirements**: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07]
**Success Criteria** (what must be TRUE):
  1. Hardened-local test suite validates all required controls.
  2. CI includes security regression coverage for hardening features.
  3. Release checklist confirms readiness for local secure usage.
**Plans**: 3

Plans:
- [x] 04-01: Build end-to-end hardening verification suite
- [x] 04-02: Integrate security regressions into CI gates
- [x] 04-03: Finalize release hardening checklist and docs

### Phase 5: Retention Phase Formal Verification
**Goal**: Close audit gap **missing `03-VERIFICATION.md`** — formal execute-phase verification aligned with `03-VALIDATION.md`, summaries, and tests.
**Depends on**: Phase 3 (substantive work complete)
**Requirements**: [REQ-05, REQ-06]
**Gap closure**: Closes requirements marked `verification_status: missing` for Phase 3 in `v1.0-MILESTONE-AUDIT.md`
**Success Criteria** (what must be TRUE):
  1. `03-VERIFICATION.md` exists with requirement trace table and PASS/passed outcome.
  2. Document references automated commands that prove REQ-05 and REQ-06 behaviors.
**Plans**: 1 plan (complete)

Plans:
- [x] 05-01: Author Phase 3 formal verification report (`03-VERIFICATION.md`)

### Phase 6: Release Phase Formal Verification
**Goal**: Close audit gap **missing `04-VERIFICATION.md`** — consolidate posture tests, docs, and CI narrative for formal milestone sign-off.
**Depends on**: Phase 4 (substantive work complete)
**Requirements**: [REQ-01, REQ-02, REQ-03, REQ-04, REQ-07]
**Gap closure**: Closes Phase 4 rows in audit requirement gaps (formal traceability)
**Success Criteria** (what must be TRUE):
  1. `04-VERIFICATION.md` exists linking `tests/test_hardening_posture.py`, `tests/test_phase4_validation.py`, operator docs, CI.
  2. REQ rows satisfied in three-source sense for milestone re-audit.
**Plans**: 1 plan (complete)

Plans:
- [x] 06-01: Author Phase 4 formal verification report (`04-VERIFICATION.md`)

**Deferred (from milestone audit, low severity):** Optional future work — align `verify-policy` with `cleanup-data` `--repo` semantics for multi-root operators; document unless product priority changes.

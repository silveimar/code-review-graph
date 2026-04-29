---
phase: 01-policy-foundation-and-threat-boundaries
verified: 2026-04-29T18:30:00Z
status: passed
score: 7/7
overrides_applied: 0
re_verification:
  previous_status: null
  previous_score: null
  gaps_closed: []
  gaps_remaining: []
  regressions: []
gaps: []
deferred:
  - truth: "CI pipeline includes dedicated hardened-local policy regression jobs"
    addressed_in: "Phase 4: Verification and Release Hardening"
    evidence: "ROADMAP Phase 4 success criteria: 'CI includes security regression coverage for hardening features'"
---

# Phase 1: Policy Foundation and Threat Boundaries — Verification Report

**Phase goal:** Define and implement centralized local-only policy enforcement.

**Verified:** 2026-04-29T18:30:00Z

**Status:** passed

**Re-verification:** No — initial verification (no prior `*-VERIFICATION.md` in this phase directory).

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Hardened local profile exists and is selectable at runtime | ✓ VERIFIED | `HardenedPolicy` defaults + `resolve_policy_for_profile`; CLI `--security-profile` sets `CRG_SECURITY_PROFILE` (`cli.py`); tests in `tests/test_policy_schema.py`, `tests/test_main.py` |
| 2 | Policy loading fails closed when config is missing or invalid | ✓ VERIFIED | `load_policy` raises `PolicyLoadError` with audit emission; `tests/test_policy_schema.py` covers missing file, invalid JSON, validation failure |
| 3 | Core graph workflows run under hardened-local without cloud credentials | ✓ VERIFIED | `TestHardenedLocalOfflineCoreWorkflows` in `tests/test_tools.py` exercises `build_or_update_graph` and `get_review_context` with cloud keys unset |
| 4 | Outbound-capable embedding paths call centralized `check_egress` before network | ✓ VERIFIED | `get_provider` → `_enforce_embedding_egress` → `check_egress` with `EMBEDDING_INPUT` (`embeddings.py`); `tests/test_embeddings.py` hardened cases |
| 5 | Hardened-local denies public cloud egress and fails closed on invalid destination / unknown operation (hardened) / invalid classification | ✓ VERIFIED | `egress_guard.py` + matrix in `tests/test_egress_guard.py` |
| 6 | Security-relevant policy actions produce local audit traces (structured JSONL) | ✓ VERIFIED | `audit.py` `emit_audit_record`; wired from `policy_loader.py`, `egress_guard.py`, `_handle_verify_policy`; `tests/test_policy_audit.py` |
| 7 | Operators can run `verify-policy` and get deterministic pass/fail (exit + output) | ✓ VERIFIED | `cli.py` `_handle_verify_policy`; codes 0/1/2; `tests/test_policy_verify.py` |

**Score:** 7/7 truths verified

### Roadmap Success Criteria (contract)

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| A | Hardened local profile exists and is selectable | ✓ | Same as truth 1 |
| B | Egress guard fails closed for protected content paths | ✓ | Embedding egress uses protected classification; invalid/missing host and unknown operations deny under hardened; only `embeddings.py` performs outbound HTTP for providers and paths are guarded |
| C | Operators can verify local-only policy status via command/output | ✓ | Same as truth 7 |

### Deferred Items

| # | Item | Addressed In | Evidence |
| --- | --- | --- | --- |
| 1 | CI wiring for hardened-local as a dedicated gate | Phase 4 | Global REQUIREMENTS acceptance criteria and ROADMAP Phase 4 SC — out of Phase 1 scope |

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `code_review_graph/security/policy_schema.py` | Strict schema + hardened defaults | ✓ VERIFIED | Pydantic models, `extra="forbid"`, egress deny default |
| `code_review_graph/security/policy_loader.py` | Fail-closed load + profile resolution | ✓ VERIFIED | `PolicyLoadError`, `resolve_policy_for_profile`, audit on load |
| `code_review_graph/security/egress_guard.py` | Central allow/deny API | ✓ VERIFIED | `check_egress`, `EgressDecision`, `_audit_and_return` |
| `code_review_graph/security/audit.py` | JSONL audit writer | ✓ VERIFIED | Required fields; pytest-safe sink |
| `code_review_graph/embeddings.py` | Guard on cloud provider paths | ✓ VERIFIED | `_enforce_embedding_egress` before each cloud branch |
| `code_review_graph/cli.py` | Profile + `verify-policy` | ✓ VERIFIED | `--security-profile`, `verify-policy` subcommand |
| `tests/test_policy_schema.py` | Schema/loader regression | ✓ VERIFIED | Present, substantive |
| `tests/test_egress_guard.py` | Decision matrix | ✓ VERIFIED | Present |
| `tests/test_embeddings.py` | Hardened egress integration | ✓ VERIFIED | `TestHardenedLocalEgressEnforcement` |
| `tests/test_policy_audit.py` | Audit contract | ✓ VERIFIED | Present |
| `tests/test_policy_verify.py` | CLI verification contract | ✓ VERIFIED | Present |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| `policy_loader.py` | `policy_schema.py` | `HardenedPolicy.model_validate` | ✓ WIRED | Validated construction |
| `tests/test_policy_schema.py` | `policy_loader.py` | `load_policy`, `resolve_policy_for_profile` | ✓ WIRED | Direct imports and calls |
| `embeddings.py` | `egress_guard.py` | `check_egress` in `_enforce_embedding_egress` | ✓ WIRED | Lines 543–558, 649–688 |
| `cli.py` | `policy_loader.py` | `resolve_policy_for_profile` in `_handle_verify_policy` | ✓ WIRED | Lines 325–326 |
| `egress_guard.py` | `audit.py` | `emit_audit_record` in `_audit_and_return` | ✓ WIRED | Lines 108–127 |

### Data-Flow Trace (Level 4)

| Artifact | Data variable | Source | Produces real data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| `verify-policy` output | `policy`, `probe`, `compliant` | `resolve_policy_for_profile` + `check_egress` probe | ✓ Effective env + resolved policy | ✓ FLOWING |
| Audit JSONL | `record` | Runtime policy events | ✓ Written when sink active | ✓ FLOWING (tests use `CRG_AUDIT_LOG_PATH` / patterns) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Phase 1 security test suites | `uv run pytest tests/test_policy_schema.py tests/test_egress_guard.py tests/test_embeddings.py tests/test_policy_audit.py tests/test_policy_verify.py -q` | 115 passed | ✓ PASS |
| Hardened CLI / offline workflow tests | `uv run pytest tests/test_tools.py -k "HardenedLocal or SecurityProfile" tests/test_main.py -k "SecurityProfile" -q` | 2 passed | ✓ PASS |

### Requirements Coverage

| Requirement | Description | Status | Evidence |
| ----------- | ----------- | ------ | -------- |
| REQ-01 | Hardened local profile disables code/content egress by default | ✓ SATISFIED | Default egress deny + `check_egress`; embedding enforcement |
| REQ-02 | Core workflows offline without cloud dependencies | ✓ SATISFIED | `TestHardenedLocalOfflineCoreWorkflows`; local default embeddings |
| REQ-06 | Local audit traces for security-relevant actions | ✓ SATISFIED | `audit.py` + loader/guard/verify emissions |
| REQ-07 | Verification path for hardened profile active and compliant | ✓ SATISFIED | `verify-policy` + tests |

**Orphaned requirements:** None — all four IDs appear in plan frontmatter (`01-01` through `01-03`).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | — | — | No blocker patterns in `code_review_graph/security/` (token `pass` in `egress_guard.py` is control-flow for standard-mode unknown operations, not an empty implementation). |

### Human Verification Required

_None — CLI and audit contracts are covered by automated tests; no visual-only or live-service behaviors required to validate Phase 1 goal._

### Gaps Summary

No gaps — Phase 1 deliverables for centralized policy enforcement, egress guard integration on current outbound paths, audit baseline, and `verify-policy` are implemented and exercised by tests.

---

_Verified: 2026-04-29T18:30:00Z_

_Verifier: Claude (gsd-verifier)_

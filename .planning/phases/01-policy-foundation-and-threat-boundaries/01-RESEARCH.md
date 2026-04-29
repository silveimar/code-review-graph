# Phase 1: Policy Foundation and Threat Boundaries - Research

**Researched:** 2026-04-29  
**Domain:** Local-only policy enforcement, egress control, fail-closed security controls  
**Confidence:** HIGH

## User Constraints

### Locked Decisions
- Build a centralized local-only policy enforcement layer for Phase 1 scope [VERIFIED: .planning/ROADMAP.md]
- Satisfy `REQ-01`, `REQ-02`, `REQ-06`, `REQ-07` in this phase [VERIFIED: .planning/ROADMAP.md]
- Focus implementation research on: local-only boundaries, outbound egress controls, fail-closed config schema, audit baseline, and deny-by-default tests [VERIFIED: user request]

### Claude's Discretion
- Choose concrete policy schema technology and module boundaries consistent with existing Python stack [VERIFIED: .planning/codebase/STACK.md]
- Recommend test strategy and verification command contract compatible with pytest/CLI patterns [VERIFIED: .planning/codebase/TESTING.md]

### Deferred Ideas (OUT OF SCOPE)
- Data-at-rest encryption implementation details (Phase 2) [VERIFIED: .planning/ROADMAP.md]
- Retention/deletion implementation details (Phase 3) [VERIFIED: .planning/ROADMAP.md]

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-01 | Hardened local profile disables code/content egress by default | Deny-by-default policy schema + centralized outbound guard pattern |
| REQ-02 | Core workflows run offline without cloud dependencies | Local provider defaults + explicit cloud provider block policy |
| REQ-06 | Produce local audit traces for security-relevant actions | Audit event contract (who/what/when/result/reason) and tamper-aware local log guidance |
| REQ-07 | Expose verification path proving hardened policy active | `verify-policy` style CLI output with guard status and active rules |

## Summary

Phase 1 should introduce a single policy authority that every outbound-capable path must call before execution, then fail closed when policy is missing, invalid, or undecidable. This aligns with OWASP authorization guidance to deny by default and centralize failed-check handling [CITED: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html]. Current code already warns when cloud embedding providers are used, but this is warning-level UX, not enforceable policy [VERIFIED: code_review_graph/embeddings.py].  

The highest-leverage implementation is: (1) define a strict config schema for hardened-local profile, (2) enforce egress decisions in one reusable guard module, (3) emit structured local audit events for all policy-relevant actions, and (4) ship explicit verification output proving effective policy. This maps directly to the roadmap’s Phase 1 success criteria and requirements [VERIFIED: .planning/ROADMAP.md][VERIFIED: .planning/REQUIREMENTS.md].  

Existing architecture already has a clean integration seam for this: CLI/MCP entry surfaces route through orchestrators and tool facades, so a shared policy guard can be injected in integration-heavy modules (initially embeddings/providers and any future HTTP integrations) with minimal coupling [VERIFIED: .planning/codebase/ARCHITECTURE.md].

**Primary recommendation:** Implement a strict, centralized `SecurityPolicy` + `EgressGuard` that defaults to deny, blocks cloud providers in hardened mode, emits structured local audit records, and exposes `verify-policy` output as a first-class operator command [VERIFIED: .planning/ROADMAP.md][CITED: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html].

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Hardened profile selection & schema validation | API / Backend (CLI+MCP service layer) | Database / Storage | Policy is process-level runtime behavior; schema is loaded locally at startup and not client-owned [VERIFIED: code_review_graph/cli.py][VERIFIED: code_review_graph/main.py] |
| Outbound egress authorization | API / Backend | — | Outbound calls originate from Python runtime modules (e.g., embeddings providers), so enforcement must occur before network attempt [VERIFIED: code_review_graph/embeddings.py] |
| Offline-mode gate for core workflows | API / Backend | Database / Storage | Build/update/query/review run in local process against SQLite graph; controls should gate optional external providers only [VERIFIED: .planning/REQUIREMENTS.md][VERIFIED: code_review_graph/graph.py] |
| Audit traces for policy events | API / Backend | Database / Storage | Event production occurs in execution paths; durable storage is local filesystem/SQLite [VERIFIED: .planning/codebase/INTEGRATIONS.md][CITED: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html] |
| Verification report surface | API / Backend | — | Operator verification is a CLI/MCP output contract, not a client-side concern [VERIFIED: .planning/ROADMAP.md][VERIFIED: code_review_graph/cli.py] |

## Project Constraints (from .cursor/rules/)

- No `.cursor/rules/` directory exists in this repository, so no additional project-specific rule directives were discovered for this phase [VERIFIED: filesystem scan of .cursor/rules].  
- Global repository constraints from `CLAUDE.md` still apply: parameterized SQL, no `shell=True`, environment-only secrets, and explicit error logging practices [VERIFIED: CLAUDE.md].

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`pathlib`, `json`, `logging`, `enum`) | 3.10+ runtime | Policy loading, local audit emission, deterministic fail-closed checks | Already core runtime; avoids new operational dependency for enforcement engine [VERIFIED: pyproject.toml][VERIFIED: code_review_graph/cli.py] |
| `pydantic` | 2.13.3 (released 2026-04-20) | Strict policy schema validation (`strict`, `extra='forbid'`) | Strong typed validation and explicit config controls reduce schema drift and fail-open risk [VERIFIED: PyPI API query][CITED: https://docs.pydantic.dev/latest/concepts/config/] |
| `pytest` | 9.0.3 (released 2026-04-07) | Deny-by-default and guard-coverage tests | Existing test framework and patterns already established in repo [VERIFIED: PyPI API query][VERIFIED: pyproject.toml] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Existing `fastmcp` integration | 3.2.4 | Expose verification and policy status via MCP tool surface | Use for machine-readable policy checks from MCP clients [VERIFIED: pyproject.toml][VERIFIED: PyPI API query] |
| Existing `sqlite3` local storage | stdlib | Optional durable audit sink beyond flat JSONL file | Use when audit query/reporting is needed beyond append-only files [VERIFIED: code_review_graph/graph.py] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Pydantic strict schema | Hand-rolled dict parsing | Faster initial coding, but higher fail-open and validation-gap risk under config evolution [CITED: https://docs.pydantic.dev/latest/concepts/config/][ASSUMED] |
| JSONL file audit sink only | SQLite audit table | Better queryability with SQLite, but slightly higher migration complexity in Phase 1 [VERIFIED: existing SQLite usage in project][ASSUMED] |

**Installation:**
```bash
uv add "pydantic>=2.13.3,<3"
```

**Version verification:**  
- `fastmcp`: 3.2.4 (PyPI upload: 2026-04-14) [VERIFIED: PyPI API query]  
- `pydantic`: 2.13.3 (PyPI upload: 2026-04-20) [VERIFIED: PyPI API query]  
- `pytest`: 9.0.3 (PyPI upload: 2026-04-07) [VERIFIED: PyPI API query]

## Architecture Patterns

### System Architecture Diagram

```text
[CLI/MCP command]
      |
      v
[PolicyLoader + SchemaValidate]
      |
      +--> (invalid/missing policy) --> [DENY + audit event + explicit error] --> [stop]
      |
      v
[EgressGuard.check(operation, destination, data_classification)]
      |
      +--> denied --> [DENY + audit event + reason code] --> [stop]
      |
      v
[Operation executes: build/update/query/embed/etc]
      |
      v
[AuditEmitter append local event]
      |
      v
[verify-policy command reads effective state]
      |
      v
[Operator-visible pass/fail report]
```

### Recommended Project Structure
```text
code_review_graph/
├── security/
│   ├── policy_schema.py      # Pydantic policy models + defaults
│   ├── policy_loader.py      # Parse/load/merge config; fail-closed behavior
│   ├── egress_guard.py       # Central allow/deny decision API
│   └── audit.py              # Structured local audit event emission
├── tools/
│   ├── verify.py             # verification report tool/CLI binding
│   └── ...                   # existing tools call security guard where needed
└── cli.py                    # add verification command route
```

### Pattern 1: Centralized Policy Decision Point
**What:** A single `EgressGuard.check(...)` function is called before any outbound-capable operation.  
**When to use:** Every network-capable integration path, including embeddings and future provider adapters.  
**Example:**
```python
# Source: repository pattern + OWASP deny-by-default guidance
decision = egress_guard.check(
    operation="embedding.request",
    destination=base_url,
    data_classification="code_content",
)
if not decision.allowed:
    audit.emit("policy_denied", decision.as_dict())
    raise PermissionError(f"Egress denied: {decision.reason}")
```

### Pattern 2: Strict Fail-Closed Policy Parsing
**What:** Policy config load fails if unknown fields or invalid values appear; runtime denies protected operations when policy cannot be trusted.  
**When to use:** Startup/load and reload boundaries for hardened mode.  
**Example:**
```python
# Source: Pydantic ConfigDict behavior
from pydantic import BaseModel, ConfigDict

class EgressPolicy(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    mode: str
    allow_localhost: bool = True
```

### Pattern 3: Security Event Contract for Audit Baseline
**What:** Emit a small mandatory schema for policy-relevant events (`when`, `who`, `what`, `result`, `reason`, `interaction_id`).  
**When to use:** Denials, policy-load failures, verification runs, and explicit cloud-allow overrides.  
**Example:**
```python
# Source: OWASP logging attributes (when/where/who/what)
event = {
    "ts": now_iso,
    "event_type": "policy_denied",
    "actor": actor,
    "operation": operation,
    "target": destination,
    "result": "deny",
    "reason": reason_code,
    "interaction_id": interaction_id,
}
```

### Anti-Patterns to Avoid
- **Per-provider ad hoc checks:** Duplicated allow/deny logic in each integration path causes drift and bypass risk [VERIFIED: current provider-specific warning logic in code_review_graph/embeddings.py].
- **Warning-only controls for egress:** Warning banners without hard denial fail `REQ-01` and can still exfiltrate content [VERIFIED: code_review_graph/embeddings.py][VERIFIED: .planning/REQUIREMENTS.md].
- **Fail-open on policy parse errors:** Continuing execution on invalid policy maps to CWE-636 style failing open risk [CITED: https://cwe.mitre.org/data/definitions/636.html].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Policy schema validation | Manual nested dict validators | Pydantic model validation | Strict type checks and forbidden extra fields are battle-tested and explicit [CITED: https://docs.pydantic.dev/latest/concepts/config/] |
| Authorization defaults | Scattered `if` checks with permissive fallbacks | Central `EgressGuard` with deny default | Central checks are easier to test and align with OWASP deny-by-default guidance [CITED: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html] |
| Audit event shape | Free-form log lines | Structured event contract (`when/where/who/what`) | Improves verification, incident analysis, and consistency [CITED: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html] |

**Key insight:** Most Phase 1 failures come from boundary inconsistency (some call paths enforce policy, others do not); centralized enforcement and structured audit are more important than sophisticated policy DSL complexity in this phase [VERIFIED: .planning/ROADMAP.md][ASSUMED].

## Common Pitfalls

### Pitfall 1: Treating “localhost exception” as blanket safe
**What goes wrong:** Code permits non-localhost domains that look local by substring matching.  
**Why it happens:** Host checks use string contains instead of parsed hostname comparisons.  
**How to avoid:** Parse hostname and compare exact loopback hosts only.  
**Warning signs:** URLs like `my-openai.127.0.0.1.nip.io` bypass checks.  
[VERIFIED: code_review_graph/embeddings.py][VERIFIED: tests/test_embeddings.py]

### Pitfall 2: Logging sensitive payloads in audit events
**What goes wrong:** Audit records accidentally include source snippets/secrets.  
**Why it happens:** Event payloads serialize raw request objects.  
**How to avoid:** Log operation metadata and reason codes, never full content fields.  
**Warning signs:** Audit lines include source code text, API keys, or large blobs.  
[CITED: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html]

### Pitfall 3: Incomplete deny-path tests
**What goes wrong:** Happy-path tests pass while denial branches remain untested.  
**Why it happens:** Existing tests focus on provider behavior and warnings, not centralized policy denial matrix.  
**How to avoid:** Parametrize allow/deny cases by operation, destination, mode, and malformed config inputs.  
**Warning signs:** No tests assert “operation aborted” under denied policy.  
[VERIFIED: tests/test_embeddings.py][VERIFIED: .planning/codebase/TESTING.md]

## Code Examples

Verified patterns from official/project sources:

### Deny-by-default enforcement call
```python
# Source: OWASP authorization guidance + project integration points
def require_egress_allowed(policy, operation, destination):
    decision = policy.egress_guard.check(operation=operation, destination=destination)
    if not decision.allowed:
        policy.audit.emit("policy_denied", decision.as_dict())
        raise PermissionError(decision.reason)
```

### Parametrized deny-matrix test
```python
# Source: pytest parametrize docs
import pytest

@pytest.mark.parametrize(
    "mode,destination,expected",
    [
        ("hardened_local", "https://api.openai.com/v1", False),
        ("hardened_local", "http://127.0.0.1:11434", True),
        ("standard", "https://api.openai.com/v1", True),
    ],
    ids=["deny-cloud", "allow-loopback", "allow-standard"],
)
def test_egress_policy_matrix(mode, destination, expected):
    assert policy_allows(mode, destination) is expected
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Provider-level warning before cloud embeddings | Centralized mandatory policy decision with deny default | Security hardening era best practice (ongoing) | Prevents warning fatigue and bypass via unchecked paths |
| Implicit config assumptions | Strict schema + explicit verification command | Modern config-hardening practices | Reduces fail-open misconfig and improves operability |

**Deprecated/outdated:**
- Warning-only cloud egress controls for protected content paths should be treated as transitional, not sufficient hardened policy [VERIFIED: code_review_graph/embeddings.py][VERIFIED: .planning/REQUIREMENTS.md].

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Adding `pydantic` is acceptable for this repo’s dependency policy and maintenance posture | Standard Stack | Medium: could force redesign to stdlib-only schema validation |
| A2 | A JSONL audit sink is sufficient baseline for Phase 1 before optional SQLite audit table | Architecture Patterns | Medium: may under-serve operator query/reporting needs |
| A3 | “Central guard first” is preferable to introducing a full policy engine DSL in this phase | Don’t Hand-Roll | Low: planner might need extra tasks if richer policy language is required immediately |

## Open Questions (RESOLVED)

1. **Scope of protected payload classes for egress blocking — RESOLVED**
   - Decision: Phase 1 treats `source_snippet`, `symbol_context`, `full_file_content`, and `embedding_input` as protected payload classes.
   - Implementation note: Policy schema includes a concrete `protected_data_classes` list with these values and default deny for cloud destinations in hardened mode.
   - Follow-up: Additional classes can be appended in future phases without weakening defaults.

2. **Audit sink format and rotation policy in Phase 1 — RESOLVED**
   - Decision: Phase 1 implements append-only local JSONL audit baseline and explicit non-sensitive event schema.
   - Deferred scope: Rotation/tamper-evidence enhancements are intentionally deferred to later lifecycle/security phases.
   - Rationale: Satisfies REQ-06 now while preserving phase boundaries from ROADMAP.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python runtime | policy/audit implementation | ✓ | 3.10.19 | — |
| `uv` | dependency/test workflow | ✓ | 0.10.4 | `pip` + `python -m pytest` |
| `git` | verification workflow + existing tooling | ✓ | 2.50.1 | — |
| Node/npm | optional tooling/docs (not core for Phase 1 impl) | ✓ | Node 24.14.1 / npm 11.11.0 | — |

**Missing dependencies with no fallback:**
- None identified for Phase 1 core implementation [VERIFIED: environment probe commands].

**Missing dependencies with fallback:**
- None identified [VERIFIED: environment probe commands].

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x in repo (latest 9.0.3 available) |
| Config file | `pyproject.toml` |
| Quick run command | `uv run pytest tests/test_main.py tests/test_embeddings.py -q` |
| Full suite command | `uv run pytest tests/ --tb=short -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-01 | Hardened profile denies cloud/code-content egress by default | unit + integration | `uv run pytest tests/test_embeddings.py -q` + new policy tests | ⚠️ Partial (add Wave 0) |
| REQ-02 | Core workflows stay offline-capable | integration | `uv run pytest tests/test_tools.py tests/test_main.py -q` + new offline policy checks | ⚠️ Partial (add Wave 0) |
| REQ-06 | Security-relevant operations emit local audit events | unit | new `uv run pytest tests/test_policy_audit.py -q` | ❌ Wave 0 |
| REQ-07 | Verification command proves hardened policy active | unit + contract | new `uv run pytest tests/test_policy_verify.py -q` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/test_main.py tests/test_embeddings.py -q`
- **Per wave merge:** `uv run pytest tests/test_main.py tests/test_embeddings.py tests/test_tools.py -q`
- **Phase gate:** `uv run pytest tests/ --tb=short -q`

### Wave 0 Gaps
- [ ] `tests/test_policy_schema.py` — strict config parsing, unknown-field rejection, fail-closed load behavior
- [ ] `tests/test_egress_guard.py` — deny-by-default matrix by mode/destination/operation
- [ ] `tests/test_policy_audit.py` — required event fields + redaction checks
- [ ] `tests/test_policy_verify.py` — operator-visible verification contract

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no (phase does not introduce user auth) | n/a |
| V3 Session Management | no (phase does not introduce session tokens) | n/a |
| V4 Access Control | yes | Central deny-by-default policy guard [CITED: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html] |
| V5 Input Validation | yes | Strict policy schema validation (`strict`, `extra='forbid'`) [CITED: https://docs.pydantic.dev/latest/concepts/config/] |
| V6 Cryptography | no (crypto-at-rest targeted in later phase) | deferred to Phase 2/3 roadmap [VERIFIED: .planning/ROADMAP.md] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Fail-open policy parse or decision errors | Elevation of Privilege | Deny on error and emit audit event with reason code [CITED: https://cwe.mitre.org/data/definitions/636.html] |
| Outbound provider bypass via unchecked integration path | Information Disclosure | Mandatory centralized `EgressGuard` call before outbound operation [VERIFIED: integration pattern in code_review_graph/embeddings.py][ASSUMED] |
| Audit log tampering/deletion | Repudiation | Append-only local logs + restricted permissions + verification checks [CITED: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html] |
| Sensitive data leakage in logs | Information Disclosure | Log metadata only; redact source content/secrets [CITED: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html] |

## Sources

### Primary (HIGH confidence)
- Repository planning docs (`.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`) — scope, requirements, phase decomposition
- Repository architecture/stack docs (`.planning/codebase/STACK.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/INTEGRATIONS.md`, `.planning/codebase/TESTING.md`, `.planning/codebase/CONCERNS.md`) — implementation baseline and risk surfaces
- Code references (`code_review_graph/embeddings.py`, `code_review_graph/main.py`, `tests/test_embeddings.py`, `tests/test_main.py`) — current egress control and test coverage realities
- PyPI JSON APIs (`https://pypi.org/pypi/fastmcp/json`, `https://pypi.org/pypi/pydantic/json`, `https://pypi.org/pypi/pytest/json`) — latest versions and release dates

### Secondary (MEDIUM confidence)
- OWASP Authorization Cheat Sheet — deny-by-default, centralized failed-check handling: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Logging Cheat Sheet — security event attributes and logging verification guidance: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- Pydantic configuration docs — strict and schema config behavior: https://docs.pydantic.dev/latest/concepts/config/
- Pytest parametrization and skip/xfail docs: https://docs.pytest.org/en/stable/example/parametrize.html and https://docs.pytest.org/en/stable/how-to/skipping.html

### Tertiary (LOW confidence)
- CWE-636 conceptual reference for fail-open risk framing: https://cwe.mitre.org/data/definitions/636.html (used as principle support; implementation details remain project-specific)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — grounded in existing repo stack + PyPI version verification
- Architecture: HIGH — derived from current module boundaries and roadmap task structure
- Pitfalls: MEDIUM — two are directly evidenced in code/tests; some mitigations are prescriptive extrapolations

**Research date:** 2026-04-29  
**Valid until:** 2026-05-29

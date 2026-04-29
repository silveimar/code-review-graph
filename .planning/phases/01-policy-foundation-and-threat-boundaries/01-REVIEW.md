---
phase: 01-policy-foundation-and-threat-boundaries
reviewed: 2026-04-29T12:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - code_review_graph/security/policy_schema.py
  - code_review_graph/security/policy_loader.py
  - code_review_graph/security/egress_guard.py
  - code_review_graph/security/audit.py
  - code_review_graph/embeddings.py
  - code_review_graph/cli.py
  - tests/test_policy_schema.py
  - tests/test_egress_guard.py
  - tests/test_policy_audit.py
  - tests/test_policy_verify.py
  - tests/test_embeddings.py
  - tests/test_tools.py
  - tests/test_main.py
findings:
  critical: 0
  warning: 5
  info: 3
  total: 8
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-04-29T12:00:00Z  
**Depth:** standard  
**Files Reviewed:** 13  
**Status:** issues_found  

## Summary

Reviewed the policy schema/loader, egress guard, audit sink, CLI `verify-policy`, embedding egress enforcement, and associated tests. The fail-closed hardened-local path and `resolve_policy_for_profile` alignment checks are coherent; `check_egress` integrates consistently with `get_provider`. No **BLOCKER** (ship-blocking) defects were identified. Several **WARNING** items affect forensic completeness, metadata accuracy, defense-in-depth for standard mode, and embedding batch correctness; **INFO** items are minor consistency/style notes.

## Critical Issues

_No critical issues identified._

## Warnings

### WR-01: Audit records dropped silently on I/O failure

**File:** `code_review_graph/security/audit.py:90-100`  
**Issue:** `mkdir` and file append failures are swallowed (`except OSError: return`). Operators receive no signal that policy_load / egress / verify events were not persisted, weakening accountability and incident response.  
**Fix:** At minimum log at `warning` level with `exc_info` (without leaking sensitive paths); optionally surface a one-shot stderr hint when `CRG_AUDIT_LOG_DEBUG=1` or equivalent.

```python
except OSError as exc:
    logger.warning("audit_write_failed path=%s", log_path, exc_info=True)
    return
```

### WR-02: Mislabeled audit metadata in `verify-policy`

**File:** `code_review_graph/cli.py:382-388`  
**Issue:** `metadata={"reason_code": report["status"]}` stores `"pass"` or `"fail"` under the key `reason_code`, overloading semantics of egress guard reason codes elsewhere (`DENY_*`, `ALLOW_*`). Downstream parsers keyed on `reason_code` may misinterpret compliance vs egress semantics.  
**Fix:** Use distinct keys, e.g. `metadata={"compliance_status": report["status"], "hardened_probe_reason": probe.reason_code}` (and keep `_scrub_metadata` allowlist in sync if persisted).

### WR-03: Standard profile does not whitelist egress operations

**File:** `code_review_graph/security/egress_guard.py:147-163`  
**Issue:** For `PolicyMode.STANDARD`, unknown `operation` strings fall through to destination-based allowance when `allow_cloud_destinations` is true. Hardened mode correctly denies unknown operations; standard mode does not. Any future caller of `check_egress` with arbitrary `operation` labels gets cloud allow without operation validation— weaker defense in depth than hardened behavior implies.  
**Fix:** If standard mode should still restrict surface area, require `op in KNOWN_EGRESS_OPERATIONS` before allowing non-local destinations, or document explicitly that only hardened mode enforces the operation registry.

### WR-04: Local embeddings use `trust_remote_code=True`

**File:** `code_review_graph/embeddings.py:76-79`  
**Issue:** `SentenceTransformer(..., trust_remote_code=True)` enables arbitrary code execution from model repositories when users point `CRG_EMBEDDING_MODEL` at untrusted or compromised checkpoints— at odds with “hardened local” expectations for otherwise offline embeddings.  
**Fix:** Default `trust_remote_code=False` for hardened deployments; gate `True` behind an explicit env flag (e.g. `CRG_EMBEDDING_TRUST_REMOTE_CODE=1`) and document the risk in CLI/help.

### WR-05: `embed_nodes` can truncate silently if batch length mismatches

**File:** `code_review_graph/embeddings.py:836-845`  
**Issue:** `zip(to_embed, vectors)` stops at the shorter iterable. If `provider.embed` returns fewer vectors than inputs (provider bug or partial failure), some nodes are skipped without error and stale embeddings may remain— correctness risk for semantic search.  
**Fix:** After `embed`, assert `len(vectors) == len(to_embed)` (or match batches explicitly) and raise `RuntimeError` on mismatch.

## Info

### IN-01: Redundant broad exception around `urlparse`

**File:** `code_review_graph/security/egress_guard.py:90-97`  
**Issue:** `urlparse` does not raise for typical malformed URLs; the `except Exception` branch is effectively dead and masks intent. Prefer removing the try/except or narrowing documentation.

### IN-02: Policy audit metadata uses basename only

**File:** `code_review_graph/security/policy_loader.py:28-74` (repeated pattern)  
**Issue:** `metadata={"policy_path": path.name}` loses directory context, making disambiguation harder when multiple repos use `policy.json`. Prefer a sanitized relative path if safe to compute.

### IN-03: Inline import in egress audit helper

**File:** `code_review_graph/security/egress_guard.py:115`  
**Issue:** `from .audit import emit_audit_record` inside `_audit_and_return` avoids circular imports but conflicts with project guidance to prefer top-level imports where possible. Acceptable if intentional; otherwise refactor module initialization order.

---

_Reviewed: 2026-04-29T12:00:00Z_  
_Reviewer: Claude (gsd-code-reviewer)_  
_Depth: standard_

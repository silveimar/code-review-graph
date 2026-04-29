# Research: Local-Only Security Foundations

## Objective
Identify security controls and design choices needed to operate the code-review graph fully local while protecting analyzed source/content.

## Core Security Domains
1. **Data locality and egress prevention**
   - Default-disable external providers for embeddings/inference when handling protected code.
   - Add explicit allowlist/denylist policy and runtime checks around outbound integrations.
   - Provide a "prove local mode" command/report showing active providers and egress guard status.

2. **Data-at-rest protection**
   - Encrypt graph database and generated artifacts where practical; otherwise enforce disk-level encryption requirement and documented hardening.
   - Protect backup/export artifacts with same policy as primary storage.
   - Minimize sensitive content persistence in caches and temp files.

3. **Runtime access control and auditing**
   - Restrict file permissions for `.code-review-graph/` and `.planning/` artifacts.
   - Add optional passphrase/profile gate for hardened operations.
   - Produce tamper-evident local audit logs for key actions (build/update/query/export).

4. **Retention and secure deletion**
   - Define retention windows by artifact type (graph DB, logs, wiki exports, temp files).
   - Implement secure cleanup routines and operator-facing commands.
   - Include verification steps that demonstrate deletion outcome.

5. **Supply chain and dependency trust**
   - Pin critical dependencies and verify checksums where possible.
   - Reduce dynamic remote fetches during runtime in hardened profile.
   - Document upgrade process that re-validates security invariants.

## Tradeoffs
- Stronger local controls can reduce convenience and performance.
- Hardening should be profile-based to preserve a standard developer mode.
- "Secure by default" in hardened mode is preferred over opt-in toggles.

## Recommendations to Carry into Requirements
- Introduce `hardened_local` profile as first-class configuration.
- Add policy enforcement layer around any outbound integration path.
- Add security-focused tests for no-egress, retention, and access control.
- Provide an operational checklist and quick verification command set.

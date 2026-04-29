"""Centralized egress authorization decisions for outbound-capable operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from urllib.parse import urlparse

from .policy_schema import (
    HardenedPolicy,
    PolicyMode,
    ProtectedDataClass,
)

# Embedding HTTP egress operations — extend when new providers are added.
KNOWN_EGRESS_OPERATIONS: Final[frozenset[str]] = frozenset({
    "embeddings.openai",
    "embeddings.google",
    "embeddings.minimax",
})

# Canonical destinations used for policy checks (must match outbound URLs).
GOOGLE_GENAI_EGRESS_URL: Final[str] = "https://generativelanguage.googleapis.com"
MINIMAX_EMBEDDINGS_EGRESS_URL: Final[str] = "https://api.minimax.io/v1/embeddings"


class EgressReasonCode:
    """Stable machine-readable reason codes for audit and tests."""

    ALLOWED_LOCAL_ENDPOINT = "allowed_local_endpoint"
    ALLOWED_STANDARD_POLICY = "allowed_standard_policy"
    ALLOWED_CLOUD_POLICY = "allowed_cloud_policy"
    DENY_CLOUD_HARDENED = "deny_cloud_hardened"
    DENY_INVALID_DESTINATION = "deny_invalid_destination"
    DENY_UNKNOWN_OPERATION = "deny_unknown_operation"
    DENY_UNKNOWN_DATA_CLASSIFICATION = "deny_unknown_data_classification"


@dataclass(frozen=True)
class EgressDecision:
    """Result of an egress authorization check."""

    allowed: bool
    reason_code: str
    reason: str

    def to_dict(self) -> dict[str, bool | str]:
        return {
            "allowed": self.allowed,
            "reason_code": self.reason_code,
            "reason": self.reason,
        }


def _normalize_classification(
    raw: str | ProtectedDataClass | None,
) -> tuple[ProtectedDataClass | None, EgressDecision | None]:
    """Return validated classification or a deny decision for invalid input."""
    if raw is None:
        return ProtectedDataClass.EMBEDDING_INPUT, None
    if isinstance(raw, ProtectedDataClass):
        return raw, None
    try:
        return ProtectedDataClass(raw), None
    except ValueError:
        return None, EgressDecision(
            allowed=False,
            reason_code=EgressReasonCode.DENY_UNKNOWN_DATA_CLASSIFICATION,
            reason="Unknown or invalid data classification for egress policy",
        )


def _hostname_is_allowed_local(hostname: str, policy: HardenedPolicy) -> bool:
    h = (hostname or "").lower()
    if h in {"127.0.0.1", "localhost", "::1", "0.0.0.0"}:
        return True
    allowed = {x.lower() for x in policy.egress.allowed_local_destinations}
    return h in allowed


def _parse_destination(destination: str) -> tuple[str | None, EgressDecision | None]:
    """Extract hostname from URL; fail closed on missing/ambiguous host."""
    dest = (destination or "").strip()
    if not dest:
        return None, EgressDecision(
            allowed=False,
            reason_code=EgressReasonCode.DENY_INVALID_DESTINATION,
            reason="Empty egress destination",
        )
    try:
        parsed = urlparse(dest)
    except Exception:
        return None, EgressDecision(
            allowed=False,
            reason_code=EgressReasonCode.DENY_INVALID_DESTINATION,
            reason="Destination could not be parsed as a URL",
        )
    host = parsed.hostname
    if not host:
        return None, EgressDecision(
            allowed=False,
            reason_code=EgressReasonCode.DENY_INVALID_DESTINATION,
            reason="Destination URL has no hostname",
        )
    return host.lower(), None


def _audit_and_return(
    policy: HardenedPolicy,
    operation: str,
    decision: EgressDecision,
    destination_host: str | None,
) -> EgressDecision:
    """Emit local audit line for egress decision, then return *decision*."""
    from .audit import emit_audit_record

    meta: dict[str, str | bool] = {"reason_code": decision.reason_code}
    if destination_host:
        meta["destination_host"] = destination_host
    emit_audit_record(
        policy,
        event_type="policy_allow" if decision.allowed else "policy_deny",
        operation=operation.strip(),
        result="allow" if decision.allowed else "deny",
        reason=decision.reason_code,
        metadata=meta,
    )
    return decision


def check_egress(
    policy: HardenedPolicy,
    *,
    operation: str,
    destination: str,
    data_classification: str | ProtectedDataClass | None = None,
) -> EgressDecision:
    """Decide whether an outbound-capable operation is allowed.

    Denies by default for hardened-local when the destination is not an
    approved local endpoint and cloud egress is disabled.
    """
    _, cls_deny = _normalize_classification(data_classification)
    if cls_deny is not None:
        return _audit_and_return(policy, operation, cls_deny, None)

    op = operation.strip()
    hardened = policy.mode == PolicyMode.HARDENED_LOCAL

    if op not in KNOWN_EGRESS_OPERATIONS:
        if hardened:
            return _audit_and_return(
                policy,
                operation,
                EgressDecision(
                    allowed=False,
                    reason_code=EgressReasonCode.DENY_UNKNOWN_OPERATION,
                    reason=f"Unknown egress operation: {operation!r}",
                ),
                None,
            )
        # Standard mode: allow only after destination validation (still block junk).
        pass

    host, parse_deny = _parse_destination(destination)
    if parse_deny is not None:
        return _audit_and_return(policy, operation, parse_deny, None)

    assert host is not None  # parse_deny would be set

    local_ok = _hostname_is_allowed_local(host, policy)

    if policy.mode == PolicyMode.STANDARD:
        if local_ok:
            return _audit_and_return(
                policy,
                operation,
                EgressDecision(
                    allowed=True,
                    reason_code=EgressReasonCode.ALLOWED_LOCAL_ENDPOINT,
                    reason="Destination is an approved local endpoint",
                ),
                host,
            )
        if policy.egress.allow_cloud_destinations:
            return _audit_and_return(
                policy,
                operation,
                EgressDecision(
                    allowed=True,
                    reason_code=EgressReasonCode.ALLOWED_STANDARD_POLICY,
                    reason="Standard profile allows cloud destinations",
                ),
                host,
            )
        return _audit_and_return(
            policy,
            operation,
            EgressDecision(
                allowed=False,
                reason_code=EgressReasonCode.DENY_CLOUD_HARDENED,
                reason="Cloud egress not allowed by egress policy",
            ),
            host,
        )

    # Hardened local
    if local_ok:
        return _audit_and_return(
            policy,
            operation,
            EgressDecision(
                allowed=True,
                reason_code=EgressReasonCode.ALLOWED_LOCAL_ENDPOINT,
                reason="Destination is an approved local endpoint",
            ),
            host,
        )
    if policy.egress.allow_cloud_destinations:
        return _audit_and_return(
            policy,
            operation,
            EgressDecision(
                allowed=True,
                reason_code=EgressReasonCode.ALLOWED_CLOUD_POLICY,
                reason="Policy explicitly allows cloud destinations",
            ),
            host,
        )
    return _audit_and_return(
        policy,
        operation,
        EgressDecision(
            allowed=False,
            reason_code=EgressReasonCode.DENY_CLOUD_HARDENED,
            reason="Hardened local profile denies cloud egress",
        ),
        host,
    )

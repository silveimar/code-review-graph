"""Fail-closed security policy loading and profile resolution."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .audit import emit_audit_record
from .policy_schema import HardenedPolicy, PolicyAction, PolicyMode


class PolicyLoadError(RuntimeError):
    """Raised when policy inputs are missing, malformed, or ambiguous."""


def load_policy(policy_path: Path | str) -> HardenedPolicy:
    """Load and validate a policy file with strict fail-closed behavior."""
    path = Path(policy_path)
    if not path.exists():
        emit_audit_record(
            None,
            event_type="policy_load_failure",
            operation="policy.load",
            result="failure",
            reason="file_missing",
            metadata={"policy_path": path.name},
        )
        raise PolicyLoadError(f"Policy file does not exist: {path}")
    if not path.is_file():
        emit_audit_record(
            None,
            event_type="policy_load_failure",
            operation="policy.load",
            result="failure",
            reason="not_a_file",
            metadata={"policy_path": path.name},
        )
        raise PolicyLoadError(f"Policy path is not a file: {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        emit_audit_record(
            None,
            event_type="policy_load_failure",
            operation="policy.load",
            result="failure",
            reason="invalid_json",
            metadata={"policy_path": path.name},
        )
        raise PolicyLoadError(f"Policy file is not valid JSON: {path}") from exc
    except OSError as exc:
        emit_audit_record(
            None,
            event_type="policy_load_failure",
            operation="policy.load",
            result="failure",
            reason="read_error",
            metadata={"policy_path": path.name},
        )
        raise PolicyLoadError(f"Unable to read policy file: {path}") from exc

    try:
        validated = HardenedPolicy.model_validate(raw)
    except ValidationError as exc:
        emit_audit_record(
            None,
            event_type="policy_load_failure",
            operation="policy.load",
            result="failure",
            reason="validation_failed",
            metadata={"policy_path": path.name},
        )
        raise PolicyLoadError(f"Policy validation failed for {path}") from exc

    emit_audit_record(
        validated,
        event_type="policy_load_success",
        operation="policy.load",
        result="success",
        reason="policy_validated",
        metadata={"policy_path": path.name},
    )
    return validated


def resolve_policy_for_profile(
    profile: str,
    config_path: Path | str | None = None,
) -> HardenedPolicy:
    """Resolve deterministic policy defaults for supported runtime profiles."""
    profile_name = profile.strip().lower()
    if profile_name not in {PolicyMode.HARDENED_LOCAL.value, PolicyMode.STANDARD.value}:
        raise PolicyLoadError(
            f"Unsupported profile '{profile}'. Expected hardened_local or standard."
        )

    if config_path is not None:
        policy = load_policy(config_path)
        if policy.mode.value != profile_name:
            raise PolicyLoadError(
                "Policy mode does not match selected profile. "
                f"profile={profile_name} policy.mode={policy.mode.value}"
            )
        return policy

    if profile_name == PolicyMode.HARDENED_LOCAL.value:
        return HardenedPolicy()

    # Standard profile is intentionally more permissive than hardened local.
    return HardenedPolicy(
        mode=PolicyMode.STANDARD,
        egress={
            "default_action": PolicyAction.ALLOW,
            "allow_cloud_destinations": True,
            "allowed_local_destinations": ["127.0.0.1", "localhost", "::1"],
        },
    )


def resolve_effective_runtime_policy() -> HardenedPolicy:
    """Resolve policy from ``CRG_SECURITY_PROFILE`` and ``CRG_SECURITY_POLICY_PATH``."""
    import os

    profile = os.environ.get("CRG_SECURITY_PROFILE", "standard").strip().lower()
    cfg = os.environ.get("CRG_SECURITY_POLICY_PATH", "").strip()
    config_path = Path(cfg) if cfg else None
    return resolve_policy_for_profile(profile, config_path=config_path)

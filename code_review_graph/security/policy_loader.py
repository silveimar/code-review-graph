"""Fail-closed security policy loading and profile resolution."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .policy_schema import HardenedPolicy, PolicyAction, PolicyMode


class PolicyLoadError(RuntimeError):
    """Raised when policy inputs are missing, malformed, or ambiguous."""


def load_policy(policy_path: Path | str) -> HardenedPolicy:
    """Load and validate a policy file with strict fail-closed behavior."""
    path = Path(policy_path)
    if not path.exists():
        raise PolicyLoadError(f"Policy file does not exist: {path}")
    if not path.is_file():
        raise PolicyLoadError(f"Policy path is not a file: {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PolicyLoadError(f"Policy file is not valid JSON: {path}") from exc
    except OSError as exc:
        raise PolicyLoadError(f"Unable to read policy file: {path}") from exc

    try:
        return HardenedPolicy.model_validate(raw)
    except ValidationError as exc:
        raise PolicyLoadError(f"Policy validation failed for {path}") from exc


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

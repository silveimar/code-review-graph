"""Tests for hardened local security policy schema and loader."""

import pytest
from pydantic import ValidationError

from code_review_graph.security import (
    AuditPolicy,
    EgressPolicy,
    HardenedPolicy,
    ProtectedDataClass,
)
from code_review_graph.security.policy_loader import (
    PolicyLoadError,
    load_policy,
    resolve_policy_for_profile,
)


def test_hardened_defaults_deny_egress_and_include_offline_classes():
    policy = HardenedPolicy()

    assert policy.mode == "hardened_local"
    assert policy.egress.default_action == "deny"
    assert policy.egress.allow_cloud_destinations is False
    assert policy.egress.allowed_local_destinations == [
        "127.0.0.1",
        "localhost",
        "::1",
    ]
    assert policy.protected_data_classes == [
        ProtectedDataClass.SOURCE_SNIPPET,
        ProtectedDataClass.SYMBOL_CONTEXT,
        ProtectedDataClass.FULL_FILE_CONTENT,
        ProtectedDataClass.EMBEDDING_INPUT,
    ]


def test_schema_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        HardenedPolicy.model_validate({"unknown_field": "boom"})


def test_schema_rejects_invalid_egress_type():
    with pytest.raises(ValidationError):
        HardenedPolicy.model_validate({"egress": "deny-all"})


def test_module_exports_stable_policy_types():
    assert HardenedPolicy.__name__ == "HardenedPolicy"
    assert EgressPolicy.__name__ == "EgressPolicy"
    assert AuditPolicy.__name__ == "AuditPolicy"


def test_loader_fails_closed_on_missing_policy_source(tmp_path):
    missing = tmp_path / "missing-policy.json"
    with pytest.raises(PolicyLoadError):
        load_policy(missing)


def test_loader_returns_deterministic_policy_for_valid_config(tmp_path):
    cfg = tmp_path / "policy.json"
    cfg.write_text(
        """
        {
          "mode": "hardened_local",
          "egress": {
            "default_action": "deny",
            "allow_cloud_destinations": false,
            "allowed_local_destinations": ["127.0.0.1", "localhost", "::1"]
          },
          "protected_data_classes": [
            "source_snippet",
            "symbol_context",
            "full_file_content",
            "embedding_input"
          ],
          "audit": {
            "enabled": true,
            "include_reason_codes": true,
            "sink": "jsonl"
          }
        }
        """.strip()
    )

    policy = load_policy(cfg)
    assert policy.mode == "hardened_local"
    assert policy.egress.default_action == "deny"
    assert policy.egress.allow_cloud_destinations is False


def test_profile_resolver_uses_hardened_defaults_without_cloud_requirements():
    policy = resolve_policy_for_profile(profile="hardened_local", config_path=None)

    assert policy.mode == "hardened_local"
    assert policy.egress.allow_cloud_destinations is False
    assert "localhost" in policy.egress.allowed_local_destinations

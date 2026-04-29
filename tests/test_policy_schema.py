"""Tests for hardened local security policy schema and loader."""

import pytest
from pydantic import ValidationError

from code_review_graph.security import (
    AuditPolicy,
    EgressPolicy,
    HardenedPolicy,
    ProtectedDataClass,
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

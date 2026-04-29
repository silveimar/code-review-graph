"""Matrix tests for centralized egress guard (hardened-local fail-closed)."""

import pytest

from code_review_graph.security.egress_guard import (
    EgressReasonCode,
    KNOWN_EGRESS_OPERATIONS,
    check_egress,
)
from code_review_graph.security.policy_loader import resolve_policy_for_profile
from code_review_graph.security.policy_schema import (
    EgressPolicy,
    HardenedPolicy,
    PolicyAction,
    PolicyMode,
    ProtectedDataClass,
)


@pytest.fixture
def hardened_policy():
    return resolve_policy_for_profile("hardened_local", config_path=None)


@pytest.fixture
def standard_policy():
    return resolve_policy_for_profile("standard", config_path=None)


class TestHardenedLocalMatrix:
    def test_denies_openai_cloud_host(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="embeddings.openai",
            destination="https://api.openai.com/v1",
            data_classification="embedding_input",
        )
        assert not d.allowed
        assert d.reason_code == EgressReasonCode.DENY_CLOUD_HARDENED

    def test_allows_local_openai_gateway(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="embeddings.openai",
            destination="http://127.0.0.1:11434/v1",
            data_classification="embedding_input",
        )
        assert d.allowed
        assert d.reason_code == EgressReasonCode.ALLOWED_LOCAL_ENDPOINT

    def test_allows_localhost_hostname(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="embeddings.openai",
            destination="http://localhost:8080/v1",
            data_classification="embedding_input",
        )
        assert d.allowed

    def test_denies_unknown_operation(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="http.custom",
            destination="https://example.com",
            data_classification="embedding_input",
        )
        assert not d.allowed
        assert d.reason_code == EgressReasonCode.DENY_UNKNOWN_OPERATION

    def test_denies_empty_destination(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="embeddings.openai",
            destination="",
            data_classification="embedding_input",
        )
        assert not d.allowed
        assert d.reason_code == EgressReasonCode.DENY_INVALID_DESTINATION

    def test_denies_invalid_destination(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="embeddings.openai",
            destination="not-a-valid-url",
            data_classification="embedding_input",
        )
        assert not d.allowed
        assert d.reason_code == EgressReasonCode.DENY_INVALID_DESTINATION

    def test_denies_bad_data_classification(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="embeddings.openai",
            destination="http://127.0.0.1:11434/v1",
            data_classification="not_a_real_class",
        )
        assert not d.allowed
        assert d.reason_code == EgressReasonCode.DENY_UNKNOWN_DATA_CLASSIFICATION

    def test_allows_cloud_when_policy_overrides(self):
        policy = HardenedPolicy(
            mode=PolicyMode.HARDENED_LOCAL,
            egress=EgressPolicy(
                default_action=PolicyAction.DENY,
                allow_cloud_destinations=True,
                allowed_local_destinations=["127.0.0.1", "localhost", "::1"],
            ),
        )
        d = check_egress(
            policy,
            operation="embeddings.minimax",
            destination="https://api.minimax.io/v1/embeddings",
            data_classification=ProtectedDataClass.EMBEDDING_INPUT,
        )
        assert d.allowed
        assert d.reason_code == EgressReasonCode.ALLOWED_CLOUD_POLICY


class TestStandardProfile:
    def test_allows_public_cloud_when_standard(self, standard_policy):
        d = check_egress(
            standard_policy,
            operation="embeddings.openai",
            destination="https://api.openai.com/v1",
            data_classification="embedding_input",
        )
        assert d.allowed
        assert d.reason_code == EgressReasonCode.ALLOWED_STANDARD_POLICY


class TestKnownOperationsContract:
    def test_embedding_operations_are_declared(self):
        assert "embeddings.openai" in KNOWN_EGRESS_OPERATIONS
        assert "embeddings.google" in KNOWN_EGRESS_OPERATIONS
        assert "embeddings.minimax" in KNOWN_EGRESS_OPERATIONS

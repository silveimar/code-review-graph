"""Retention policy schema and loader compatibility (Phase 03-01)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from code_review_graph.security.policy_loader import load_policy
from code_review_graph.security.policy_schema import HardenedPolicy, RetentionPolicy


def test_retention_defaults_unlimited() -> None:
    p = HardenedPolicy()
    assert p.retention.audit_log is None
    assert p.retention.memory_artifacts is None
    assert p.retention.wiki_outputs is None
    assert p.retention.graph_derived is None


def test_retention_round_trip_json() -> None:
    p = HardenedPolicy(
        retention=RetentionPolicy(
            audit_log=30,
            memory_artifacts=14,
            wiki_outputs=60,
            graph_derived=90,
        )
    )
    raw = p.model_dump(mode="json")
    p2 = HardenedPolicy.model_validate(raw)
    assert p2.retention.audit_log == 30
    assert p2.retention.memory_artifacts == 14


def test_extra_forbid_on_hardened_policy() -> None:
    base = HardenedPolicy().model_dump(mode="json")
    base["unknown_top_level"] = True
    with pytest.raises(ValidationError):
        HardenedPolicy.model_validate(base)


def test_extra_forbid_on_retention_policy() -> None:
    with pytest.raises(ValidationError):
        RetentionPolicy.model_validate({"audit_log": 1, "extra_field": 2})


def test_retention_negative_rejected() -> None:
    with pytest.raises(ValidationError):
        RetentionPolicy(audit_log=0)


def test_load_policy_without_retention_block(tmp_path: Path) -> None:
    path = tmp_path / "pol.json"
    path.write_text(
        json.dumps(
            {
                "mode": "hardened_local",
                "egress": {
                    "default_action": "deny",
                    "allow_cloud_destinations": False,
                    "allowed_local_destinations": ["127.0.0.1"],
                },
                "audit": {"enabled": True, "include_reason_codes": True, "sink": "jsonl"},
                "artifact_encryption": {
                    "enabled": False,
                    "require_encryption": False,
                    "key_env_var": "CRG_ARTIFACT_ENCRYPTION_KEY",
                },
            }
        ),
        encoding="utf-8",
    )
    loaded = load_policy(path)
    assert loaded.retention.audit_log is None

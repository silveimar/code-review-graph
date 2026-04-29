"""Phase 2 structured audit emission tests (REQ-06)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from code_review_graph.graph import GraphStore
from code_review_graph.security.artifact_crypto import EncryptionRequiredError
from code_review_graph.security.audit import emit_phase2_artifact_encryption_event
from code_review_graph.security.policy_schema import (
    ArtifactEncryptionPolicy,
    HardenedPolicy,
)


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


@pytest.fixture
def audit_log(tmp_path, monkeypatch):
    log = tmp_path / "audit.jsonl"
    monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    return log


class TestPhase2Taxonomy:
    def test_emit_phase2_encryption_shape(self, audit_log, monkeypatch):
        monkeypatch.delenv("CRG_ARTIFACT_ENCRYPTION_KEY", raising=False)
        pol = HardenedPolicy()
        emit_phase2_artifact_encryption_event(
            pol,
            operation="artifact.encryption.gate",
            result="failure",
            reason="test_reason",
            event_subtype="unit_test",
        )
        lines = _jsonl(audit_log)
        assert len(lines) == 1
        ev = lines[0]
        assert ev["event_type"] == "artifact_encryption"
        assert ev["operation"] == "artifact.encryption.gate"
        assert ev["metadata"]["event_subtype"] == "unit_test"

    def test_graph_open_denial_emits_audit(
        self, tmp_path, audit_log, monkeypatch,
    ):
        monkeypatch.delenv("CRG_ARTIFACT_ENCRYPTION_KEY", raising=False)
        db = tmp_path / "g.db"
        pol = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(
                enabled=True,
                require_encryption=True,
            ),
        )
        with pytest.raises(EncryptionRequiredError):
            GraphStore(db, policy=pol)
        lines = _jsonl(audit_log)
        assert any(
            x.get("event_type") == "artifact_encryption"
            and x.get("result") == "failure"
            for x in lines
        )

"""Contract tests for local policy audit emission (REQ-06)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from code_review_graph.security.audit import (
    REQUIRED_FIELDS,
    emit_audit_record,
    resolve_audit_log_path,
)
from code_review_graph.security.egress_guard import check_egress
from code_review_graph.security.policy_loader import PolicyLoadError, load_policy
from code_review_graph.security.policy_schema import HardenedPolicy, PolicyMode


def _jsonl_lines(path: Path) -> list[dict]:
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


class TestAuditSchema:
    def test_emit_includes_mandatory_fields(self, audit_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        policy = HardenedPolicy()
        emit_audit_record(
            policy,
            event_type="policy_load_success",
            operation="policy.load",
            result="success",
            reason="validated",
            metadata={"policy_path": "x.json"},
        )
        lines = _jsonl_lines(audit_log)
        assert len(lines) == 1
        ev = lines[0]
        for k in REQUIRED_FIELDS:
            assert k in ev, f"missing {k}"
        assert ev["event_type"] == "policy_load_success"
        assert ev["operation"] == "policy.load"
        assert ev["result"] == "success"
        assert ev["reason"] == "validated"

    def test_metadata_excludes_raw_policy_body(self, audit_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        policy = HardenedPolicy()
        emit_audit_record(
            policy,
            event_type="policy_load_failure",
            operation="policy.load",
            result="failure",
            reason="invalid_json",
            metadata={"policy_path": "p.json"},
        )
        text = audit_log.read_text(encoding="utf-8")
        assert "secret_key" not in text
        assert '"mode"' not in text or "hardened_local" not in text  # no full policy dump


class TestPolicyLoadAudit:
    def test_load_success_emits_audit_line(self, tmp_path, monkeypatch):
        log = tmp_path / "a.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        p = tmp_path / "pol.json"
        p.write_text(
            json.dumps({"mode": "hardened_local"}),
            encoding="utf-8",
        )
        policy = load_policy(p)
        assert policy.mode == PolicyMode.HARDENED_LOCAL
        lines = _jsonl_lines(log)
        assert any(x.get("event_type") == "policy_load_success" for x in lines)

    def test_load_failure_emits_audit_line(self, tmp_path, monkeypatch):
        log = tmp_path / "a.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        p = tmp_path / "bad.json"
        p.write_text("{not json", encoding="utf-8")
        with pytest.raises(PolicyLoadError):
            load_policy(p)
        lines = _jsonl_lines(log)
        assert any(x.get("event_type") == "policy_load_failure" for x in lines)


class TestEgressAudit:
    def test_allow_emits_policy_allow(self, audit_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        policy = HardenedPolicy()
        check_egress(
            policy,
            operation="embeddings.openai",
            destination="http://127.0.0.1:11434/v1",
        )
        lines = _jsonl_lines(audit_log)
        assert any(x.get("event_type") == "policy_allow" for x in lines)

    def test_deny_emits_policy_deny(self, audit_log, monkeypatch):
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        policy = HardenedPolicy()
        check_egress(
            policy,
            operation="embeddings.openai",
            destination="https://api.openai.com/v1",
        )
        lines = _jsonl_lines(audit_log)
        assert any(x.get("event_type") == "policy_deny" for x in lines)


class TestResolveAuditLogPath:
    def test_env_overrides_default(self, monkeypatch, tmp_path):
        log = tmp_path / "custom.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        assert resolve_audit_log_path() == log.resolve()


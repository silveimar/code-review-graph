"""CLI policy verification contract tests (REQ-07)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from code_review_graph.cli import main


def _run(argv: list[str], monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", argv)
    exc = None
    try:
        main()
    except SystemExit as e:
        exc = e
    out = capsys.readouterr().out
    err = capsys.readouterr().err
    code = exc.code if exc is not None else 0
    if isinstance(code, str):
        code = int(code)
    return code, out, err


class TestVerifyPolicySuccess:
    def test_hardened_local_passes_exit_zero(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("CRG_SECURITY_POLICY_PATH", raising=False)
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "hardened_local")
        log = tmp_path / "a.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        code, out, _ = _run(["code-review-graph", "verify-policy"], monkeypatch, capsys)
        assert code == 0
        assert "PASS" in out or "pass" in out.lower()
        assert "hardened_local" in out

    def test_json_output_includes_compliance_fields(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("CRG_SECURITY_POLICY_PATH", raising=False)
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "hardened_local")
        log = tmp_path / "a.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        code, out, _ = _run(
            ["code-review-graph", "verify-policy", "--json"],
            monkeypatch,
            capsys,
        )
        assert code == 0
        data = json.loads(out.strip())
        assert data.get("compliant") is True
        assert "active_profile" in data
        assert "egress" in data
        assert "retention" in data
        ret = data["retention"]
        assert ret.get("cleanup_command") == "code-review-graph cleanup-data"
        assert "audit_log_max_age_days" in ret


class TestVerifyPolicyFailure:
    def test_standard_profile_fails_nonzero(self, monkeypatch, capsys, tmp_path):
        monkeypatch.delenv("CRG_SECURITY_POLICY_PATH", raising=False)
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "standard")
        log = tmp_path / "a.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        code, out, _ = _run(["code-review-graph", "verify-policy"], monkeypatch, capsys)
        assert code != 0
        assert "FAIL" in out or "fail" in out.lower()

    def test_invalid_policy_path_fails(self, monkeypatch, capsys, tmp_path):
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "hardened_local")
        monkeypatch.setenv("CRG_SECURITY_POLICY_PATH", str(tmp_path / "nonexistent.json"))
        log = tmp_path / "a.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        code, _, _ = _run(["code-review-graph", "verify-policy"], monkeypatch, capsys)
        assert code != 0

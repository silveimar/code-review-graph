"""Orchestrated hardened-local posture checks (Phase 4 — REQ-01–REQ-07 integration).

Subprocess exercises real CLI entry (`python -m code_review_graph verify-policy --json`).
In-process checks reuse security APIs aligned with tests/test_egress_guard.py.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from code_review_graph.security.egress_guard import EgressReasonCode, check_egress
from code_review_graph.security.policy_loader import resolve_policy_for_profile

pytestmark = pytest.mark.hardening_posture

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def hardened_policy():
    return resolve_policy_for_profile("hardened_local", config_path=None)


class TestHardeningPostureSubprocess:
    """REQ-07: verification path via real subprocess CLI."""

    def test_verify_policy_json_subprocess(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CRG_SECURITY_POLICY_PATH", raising=False)
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        log = tmp_path / "audit.jsonl"
        env = {
            **os.environ,
            "CRG_SECURITY_PROFILE": "hardened_local",
            "CRG_AUDIT_LOG_PATH": str(log),
        }
        env.pop("CRG_SECURITY_POLICY_PATH", None)
        env.pop("PYTEST_CURRENT_TEST", None)
        proc = subprocess.run(
            [sys.executable, "-m", "code_review_graph", "verify-policy", "--json"],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        data = json.loads(proc.stdout.strip())
        assert data.get("compliant") is True
        assert "hardened_local" in str(data.get("active_profile", "")).lower()
        assert "egress" in data
        assert "retention" in data


class TestHardeningPostureInProcess:
    """Spot-check egress fail-closed without duplicating full egress matrix."""

    def test_denies_openai_cloud_host(self, hardened_policy):
        d = check_egress(
            hardened_policy,
            operation="embeddings.openai",
            destination="https://api.openai.com/v1",
            data_classification="embedding_input",
        )
        assert not d.allowed
        assert d.reason_code == EgressReasonCode.DENY_CLOUD_HARDENED

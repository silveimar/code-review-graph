"""Tests for POSIX data-dir permission hardening (Phase 02-02)."""

from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest

from code_review_graph.cli import main
from code_review_graph.incremental import get_data_dir
from code_review_graph.security.fs_permissions import (
    apply_hardened_data_dir_permissions,
    verify_data_dir_permissions,
)


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX chmod not applicable")
class TestFsPermissionsHelper:
    def test_apply_sets_modes(self, tmp_path):
        d = tmp_path / ".code-review-graph"
        d.mkdir()
        f = d / "f.txt"
        f.write_text("x", encoding="utf-8")
        sub = d / "sub"
        sub.mkdir()

        apply_hardened_data_dir_permissions(d)

        assert stat.S_IMODE(d.stat().st_mode) == 0o700
        assert stat.S_IMODE(f.stat().st_mode) == 0o600
        assert stat.S_IMODE(sub.stat().st_mode) == 0o700

    def test_verify_ok_after_apply(self, tmp_path):
        d = tmp_path / "crg"
        d.mkdir()
        (d / "graph.db").write_bytes(b"x")
        apply_hardened_data_dir_permissions(d)
        rep = verify_data_dir_permissions(d)
        assert rep["keyword"] == "FS_PERMISSIONS_OK"
        assert rep["status"] == "ok"


class TestFsIntegrationDataDir:
    @pytest.mark.skipif(sys.platform == "win32", reason="POSIX chmod")
    def test_get_data_dir_applies_when_hardened_profile(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "hardened_local")
        monkeypatch.delenv("CRG_DATA_DIR", raising=False)
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()

        dd = get_data_dir(repo)
        assert dd.exists()
        assert stat.S_IMODE(dd.stat().st_mode) == 0o700


class TestVerifyPolicyFsLine:
    def test_verify_policy_json_includes_filesystem_permissions(
        self, monkeypatch, capsys, tmp_path,
    ):
        import sys as sys_mod

        monkeypatch.delenv("CRG_SECURITY_POLICY_PATH", raising=False)
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "hardened_local")
        log = tmp_path / "a.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        repo = tmp_path / "r"
        repo.mkdir()
        (repo / ".git").mkdir()
        monkeypatch.chdir(repo)

        monkeypatch.setattr(sys_mod, "argv", ["code-review-graph", "verify-policy", "--json"])
        with pytest.raises(SystemExit) as ei:
            main()
        assert int(ei.value.code) == 0
        out = capsys.readouterr().out
        data = json.loads(out.strip())
        assert "filesystem_permissions" in data
        assert "keyword" in data["filesystem_permissions"]

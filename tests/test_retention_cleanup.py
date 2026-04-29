"""Retention cleanup evaluation and CLI (Phase 03-02)."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

from code_review_graph.cli import main
from code_review_graph.security.policy_schema import HardenedPolicy, RetentionPolicy
from code_review_graph.security.retention_eval import evaluate_retention_candidates


def _touch_days_old(path: Path, days: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    old = time.time() - days * 86400
    os.utime(path, (old, old))


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


class TestRetentionEval:
    def test_candidates_memory_over_age(self, tmp_path: Path) -> None:
        data = tmp_path / ".code-review-graph"
        mem = data / "memory"
        _touch_days_old(mem / "old.md", 10.0)
        _touch_days_old(mem / "new.md", 0.5)

        policy = HardenedPolicy(
            retention=RetentionPolicy(
                audit_log=None,
                memory_artifacts=3,
                wiki_outputs=None,
                graph_derived=None,
            )
        )
        cands = evaluate_retention_candidates(policy, data)
        paths = {c.path.name for c in cands if c.sink == "memory_artifacts"}
        assert "old.md" in paths
        assert "new.md" not in paths

    def test_dry_run_no_deletes(self, monkeypatch, capsys, tmp_path: Path) -> None:
        monkeypatch.delenv("CRG_SECURITY_POLICY_PATH", raising=False)
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "hardened_local")
        log = tmp_path / "audit.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        data = tmp_path / ".code-review-graph"
        mem = data / "memory"
        _touch_days_old(mem / "stale.md", 100.0)

        monkeypatch.setenv("CRG_REPO_ROOT", str(tmp_path))

        policy = tmp_path / "pol.json"
        from code_review_graph.security.policy_schema import HardenedPolicy as HP

        hp = HP(retention=RetentionPolicy(memory_artifacts=30))
        policy.write_text(
            json.dumps(hp.model_dump(mode="json")),
            encoding="utf-8",
        )
        monkeypatch.setenv("CRG_SECURITY_POLICY_PATH", str(policy))

        stale = mem / "stale.md"
        assert stale.is_file()

        code, out, _ = _run(
            ["code-review-graph", "cleanup-data", "--repo", str(tmp_path)],
            monkeypatch,
            capsys,
        )
        assert code == 0
        assert "dry-run" in out.lower()
        assert stale.is_file()


class TestCleanupApply:
    def test_apply_removes_and_audits(self, monkeypatch, capsys, tmp_path: Path) -> None:
        monkeypatch.delenv("CRG_SECURITY_POLICY_PATH", raising=False)
        monkeypatch.setenv("CRG_SECURITY_PROFILE", "hardened_local")
        log = tmp_path / "audit.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        monkeypatch.setenv("CRG_REPO_ROOT", str(tmp_path))

        data = tmp_path / ".code-review-graph"
        mem = data / "memory"
        f = mem / "gone.md"
        _touch_days_old(f, 200.0)

        pol = tmp_path / "pol.json"
        hp = HardenedPolicy(
            retention=RetentionPolicy(
                memory_artifacts=10,
            )
        )
        pol.write_text(json.dumps(hp.model_dump(mode="json")), encoding="utf-8")
        monkeypatch.setenv("CRG_SECURITY_POLICY_PATH", str(pol))

        assert f.is_file()
        code, out, _ = _run(
            [
                "code-review-graph",
                "cleanup-data",
                "--repo",
                str(tmp_path),
                "--apply",
            ],
            monkeypatch,
            capsys,
        )
        assert code == 0
        assert "removed" in out.lower()
        assert not f.exists()
        log_text = log.read_text(encoding="utf-8")
        assert "retention_cleanup" in log_text

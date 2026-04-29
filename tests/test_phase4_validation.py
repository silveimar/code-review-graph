"""Nyquist validation hooks for Phase 4 (docs + marker registry — REQ coverage audit)."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_registers_hardening_posture_marker():
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "hardening_posture" in text
    assert "[tool.pytest.ini_options]" in text


def test_ci_security_regression_doc_exists_and_links_workflow():
    p = REPO_ROOT / "docs" / "ci-security-regression.md"
    assert p.is_file()
    body = p.read_text(encoding="utf-8")
    assert ".github/workflows/ci.yml" in body
    assert "lint" in body.lower() or "`lint`" in body


def test_security_release_checklist_exists_and_req07():
    p = REPO_ROOT / "docs" / "security-release-checklist.md"
    assert p.is_file()
    body = p.read_text(encoding="utf-8")
    assert "verify-policy" in body
    assert "REQ-07" in body

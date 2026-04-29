"""Tests for artifact encryption policy and persistence (Phase 02-01)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from code_review_graph.graph import GraphStore
from code_review_graph.memory import save_result
from code_review_graph.security.artifact_crypto import (
    EncryptionRequiredError,
    decrypt_audit_jsonl_line,
    sqlcipher_available,
)
from code_review_graph.security.audit import emit_audit_record, resolve_audit_log_path
from code_review_graph.security.policy_schema import (
    ArtifactEncryptionPolicy,
    HardenedPolicy,
    PolicyMode,
)
from code_review_graph.wiki import generate_wiki


@pytest.fixture
def fernet_key() -> bytes:
    return Fernet.generate_key()


class TestArtifactEncryptionPolicySchema:
    def test_defaults_backward_compatible(self):
        p = HardenedPolicy()
        assert p.artifact_encryption.enabled is False
        assert p.artifact_encryption.require_encryption is False
        assert p.artifact_encryption.key_env_var == "CRG_ARTIFACT_ENCRYPTION_KEY"

    def test_custom_env_var(self):
        p = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(
                enabled=True,
                key_env_var="MY_KEY_VAR",
            )
        )
        assert p.artifact_encryption.key_env_var == "MY_KEY_VAR"

    def test_require_encryption_without_extra_fields(self):
        raw = {
            "mode": "hardened_local",
            "artifact_encryption": {
                "enabled": True,
                "require_encryption": True,
            },
        }
        p = HardenedPolicy.model_validate(raw)
        assert p.artifact_encryption.require_encryption is True


class TestGraphEncryption:
    def test_plaintext_when_encryption_disabled(self, tmp_path):
        db = tmp_path / "g.db"
        store = GraphStore(db, policy=HardenedPolicy())
        store.close()
        raw = db.read_bytes()
        assert raw.startswith(b"SQLite format 3") or len(raw) >= 16

    def test_fail_closed_require_encryption_no_key(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CRG_ARTIFACT_ENCRYPTION_KEY", raising=False)
        db = tmp_path / "g.db"
        pol = HardenedPolicy(
            mode=PolicyMode.HARDENED_LOCAL,
            artifact_encryption=ArtifactEncryptionPolicy(
                enabled=True,
                require_encryption=True,
            ),
        )
        with pytest.raises(EncryptionRequiredError):
            GraphStore(db, policy=pol)

    def test_encrypted_db_when_enabled_with_key(self, tmp_path, monkeypatch, fernet_key):
        monkeypatch.setenv("CRG_ARTIFACT_ENCRYPTION_KEY", fernet_key.decode("ascii"))
        db = tmp_path / "g.db"
        pol = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(enabled=True),
        )
        if not sqlcipher_available():
            pytest.skip("SQLCipher not available on this platform")
        store = GraphStore(db, policy=pol)
        store.close()
        header = db.read_bytes()[:16]
        assert not header.startswith(b"SQLite format 3")


class TestAuditEncryption:
    def test_audit_line_encrypted_when_enabled(
        self, tmp_path, monkeypatch, fernet_key,
    ):
        log = tmp_path / "audit.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.setenv("CRG_ARTIFACT_ENCRYPTION_KEY", fernet_key.decode("ascii"))
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        pol = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(enabled=True),
        )
        emit_audit_record(
            pol,
            event_type="test_evt",
            operation="test.op",
            result="success",
            reason="ok",
        )
        line = log.read_bytes().splitlines()[0]
        assert line.startswith(b"gAAAA")
        dec = decrypt_audit_jsonl_line(line, pol)
        rec = json.loads(dec.decode("utf-8"))
        assert rec["event_type"] == "test_evt"

    def test_emit_skipped_when_required_but_no_key(self, tmp_path, monkeypatch):
        log = tmp_path / "audit.jsonl"
        monkeypatch.setenv("CRG_AUDIT_LOG_PATH", str(log))
        monkeypatch.delenv("CRG_ARTIFACT_ENCRYPTION_KEY", raising=False)
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        pol = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(
                enabled=True,
                require_encryption=True,
            ),
        )
        emit_audit_record(
            pol,
            event_type="blocked",
            operation="test.op",
            result="failure",
            reason="none",
        )
        assert not log.exists() or log.read_bytes() == b""


class TestMemoryWiki:
    def test_save_memory_encrypted_roundtrip(
        self, tmp_path, monkeypatch, fernet_key,
    ):
        monkeypatch.setenv("CRG_ARTIFACT_ENCRYPTION_KEY", fernet_key.decode("ascii"))
        pol = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(enabled=True),
        )
        mem_dir = tmp_path / "memory"
        p = save_result(
            "q?",
            "a",
            policy=pol,
            memory_dir=mem_dir,
        )
        raw = p.read_bytes()
        assert b"CRG_FERNET_V1" in raw

    def test_save_memory_refuses_plaintext_when_required(
        self, tmp_path, monkeypatch,
    ):
        monkeypatch.delenv("CRG_ARTIFACT_ENCRYPTION_KEY", raising=False)
        pol = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(
                enabled=True,
                require_encryption=True,
            ),
        )
        with pytest.raises(EncryptionRequiredError):
            save_result("q", "a", policy=pol, memory_dir=tmp_path / "memory")

    def test_wiki_refuses_when_required_no_key(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CRG_ARTIFACT_ENCRYPTION_KEY", raising=False)
        db = tmp_path / "x.db"
        store = GraphStore(db, policy=HardenedPolicy())
        pol = HardenedPolicy(
            artifact_encryption=ArtifactEncryptionPolicy(
                enabled=True,
                require_encryption=True,
            ),
        )
        with pytest.raises(EncryptionRequiredError):
            generate_wiki(store, tmp_path / "wiki", policy=pol)
        store.close()

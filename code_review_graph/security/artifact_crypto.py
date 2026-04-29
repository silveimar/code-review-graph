"""Application-layer encryption for local artifacts (REQ-03, D-01–D-03)."""

from __future__ import annotations

import base64
import binascii
import logging
import os
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

from .policy_schema import HardenedPolicy

logger = logging.getLogger(__name__)

_FILE_MAGIC = "CRG_FERNET_V1"
_PREFIX = f"{_FILE_MAGIC}\n"

try:
    import sqlcipher3.dbapi2 as _sqlcipher
except Exception:  # noqa: BLE001 - optional native module
    _sqlcipher = None  # type: ignore[misc, assignment]


class EncryptionRequiredError(RuntimeError):
    """Raised when protected artifacts cannot be read or written per policy (D-03)."""


def _audit_encrypt_gate_failure(
    policy: HardenedPolicy,
    *,
    event_subtype: str,
    reason: str,
) -> None:
    try:
        from .audit import emit_phase2_artifact_encryption_event

        emit_phase2_artifact_encryption_event(
            policy,
            operation="artifact.encryption.gate",
            result="failure",
            reason=reason,
            event_subtype=event_subtype,
        )
    except Exception:  # noqa: BLE001 — audit must never break crypto path
        return


def sqlcipher_available() -> bool:
    return _sqlcipher is not None


def _fernet_for_policy(policy: HardenedPolicy) -> Fernet | None:
    """Return a Fernet instance or None if encryption is not configured for writes."""
    ae = policy.artifact_encryption
    if not ae.enabled:
        return None
    raw = os.environ.get(ae.key_env_var, "").strip()
    if not raw:
        return None
    try:
        return Fernet(raw.encode("ascii"))
    except (ValueError, TypeError) as exc:
        logger.warning("Invalid artifact encryption key material: %s", exc)
        return None


def fernet_key_configured(policy: HardenedPolicy) -> bool:
    """True when the configured env var holds a usable Fernet key."""
    return _fernet_for_policy(policy) is not None


def artifact_writes_must_encrypt(policy: HardenedPolicy) -> bool:
    """True when file payloads under policy must be ciphertext (enabled + valid key)."""
    ae = policy.artifact_encryption
    return ae.enabled and fernet_key_configured(policy)


def refuse_sensitive_plaintext(policy: HardenedPolicy) -> bool:
    """True when plaintext persistence for sensitive artifacts must be refused (D-03)."""
    ae = policy.artifact_encryption
    if not ae.enabled:
        return False
    if ae.require_encryption and not fernet_key_configured(policy):
        return True
    return False


def encrypt_optional_plaintext(data: bytes, policy: HardenedPolicy) -> bytes:
    """Encrypt *data* when policy requires; otherwise return unchanged."""
    if not artifact_writes_must_encrypt(policy):
        return data
    fnt = _fernet_for_policy(policy)
    assert fnt is not None
    token = fnt.encrypt(data)
    return _PREFIX.encode("utf-8") + token + b"\n"


def decrypt_optional_payload(raw: bytes, policy: HardenedPolicy) -> bytes:
    """Decrypt payload written by :func:`encrypt_optional_plaintext` if wrapped."""
    magic_b = (_FILE_MAGIC + "\n").encode("utf-8")
    if raw.startswith(magic_b):
        body = raw[len(magic_b) :].strip()
        fnt = _fernet_for_policy(policy)
        if fnt is None:
            raise EncryptionRequiredError(
                "Cannot decrypt artifact: encryption key not configured"
            )
        try:
            return fnt.decrypt(body)
        except InvalidToken as exc:
            raise EncryptionRequiredError("Artifact ciphertext invalid or tampered") from exc
    return raw


def encrypt_audit_jsonl_line(json_line: bytes, policy: HardenedPolicy) -> bytes:
    """Encrypt one JSONL record line when artifact encryption is active."""
    if not artifact_writes_must_encrypt(policy):
        return json_line
    fnt = _fernet_for_policy(policy)
    assert fnt is not None
    token = fnt.encrypt(json_line.rstrip(b"\n"))
    return token + b"\n"


def decrypt_audit_jsonl_line(line: bytes, policy: HardenedPolicy) -> bytes:
    """Decrypt a single audit JSONL physical line."""
    line = line.strip()
    if not line.startswith(b"gAAAA"):
        return line + b"\n"
    fnt = _fernet_for_policy(policy)
    if fnt is None:
        raise EncryptionRequiredError("Cannot decrypt audit line: key missing")
    try:
        return fnt.decrypt(line) + b"\n"
    except InvalidToken as exc:
        raise EncryptionRequiredError("Audit ciphertext invalid") from exc


def _fernet_key_bytes_for_sqlcipher(policy: HardenedPolicy) -> bytes | None:
    if not policy.artifact_encryption.enabled:
        return None
    ae = policy.artifact_encryption
    raw = os.environ.get(ae.key_env_var, "").strip()
    if not raw:
        return None
    try:
        kb = base64.urlsafe_b64decode(raw.encode("ascii"))
    except (ValueError, binascii.Error) as exc:
        logger.warning("Could not decode Fernet key for SQLCipher: %s", exc)
        return None
    if len(kb) != 32:
        logger.warning("Artifact encryption key decoded length != 32 bytes")
        return None
    return kb


def open_graph_sqlite_connection(db_path: Path, policy: HardenedPolicy) -> sqlite3.Connection:
    """Open SQLite or SQLCipher connection according to ``artifact_encryption`` policy."""
    ae = policy.artifact_encryption
    key_ok = fernet_key_configured(policy)
    key_material = _fernet_key_bytes_for_sqlcipher(policy)

    if ae.require_encryption:
        if not key_ok:
            _audit_encrypt_gate_failure(
                policy,
                event_subtype="require_encryption_no_key",
                reason="missing_or_invalid_key",
            )
            raise EncryptionRequiredError(
                "Artifact encryption required but key missing or invalid "
                f"(set {ae.key_env_var})"
            )
        if not sqlcipher_available():
            _audit_encrypt_gate_failure(
                policy,
                event_subtype="sqlcipher_unavailable",
                reason="driver_missing",
            )
            raise EncryptionRequiredError(
                "Artifact encryption required but SQLCipher driver is unavailable"
            )

    if ae.enabled and key_ok:
        if not sqlcipher_available():
            _audit_encrypt_gate_failure(
                policy,
                event_subtype="sqlcipher_unavailable",
                reason="driver_missing",
            )
            raise EncryptionRequiredError(
                "Artifact encryption is enabled with a valid key but SQLCipher "
                "is not available; cannot encrypt graph.db"
            )
        assert key_material is not None and _sqlcipher is not None
        hex_key = key_material.hex()
        conn = _sqlcipher.connect(
            str(db_path),
            timeout=30,
            check_same_thread=False,
            isolation_level=None,
        )
        conn.row_factory = _sqlcipher.Row
        conn.execute(f'PRAGMA key = "x\'{hex_key}\'"')
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    conn = sqlite3.connect(
        str(db_path),
        timeout=30,
        check_same_thread=False,
        isolation_level=None,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

"""Structured local audit events for security-relevant policy actions (REQ-06)."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifact_crypto import (
    artifact_writes_must_encrypt,
    encrypt_audit_jsonl_line,
    refuse_sensitive_plaintext,
)
from .policy_schema import HardenedPolicy

REQUIRED_FIELDS: tuple[str, ...] = (
    "timestamp",
    "event_type",
    "operation",
    "result",
    "reason",
)

_write_lock = threading.Lock()


def resolve_audit_log_path() -> Path:
    """Default: ``.code-review-graph/policy_audit.jsonl`` under the current working directory."""
    env = os.environ.get("CRG_AUDIT_LOG_PATH", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (Path.cwd() / ".code-review-graph" / "policy_audit.jsonl").resolve()


def _file_sink_active() -> bool:
    """Suppress default file sink during pytest runs unless ``CRG_AUDIT_LOG_PATH`` is set."""
    if os.environ.get("CRG_AUDIT_LOG_PATH", "").strip():
        return True
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return False
    return True


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _scrub_metadata(meta: dict[str, Any] | None) -> dict[str, Any]:
    """Keep metadata small and non-sensitive (no config bodies or source)."""
    if not meta:
        return {}
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if v is None:
            continue
        if k in {"policy_path", "destination_host", "reason_code", "event_subtype"} and isinstance(
            v, str
        ):
            out[k] = v
        elif k in {"allowed"} and isinstance(v, bool):
            out[k] = v
        elif k == "path_hint" and isinstance(v, str):
            out[k] = Path(v).name if v else v
    return out


_PHASE2_EVENT_TYPES_PLAINTEXT_OK = frozenset(
    {"artifact_encryption", "filesystem_permissions"}
)


def emit_audit_record(
    policy: HardenedPolicy | None,
    *,
    event_type: str,
    operation: str,
    result: str,
    reason: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Append one JSONL audit record. Respects ``policy.audit`` when *policy* is set."""
    if policy is not None and not policy.audit.enabled:
        return
    if not _file_sink_active():
        return
    if policy is not None and refuse_sensitive_plaintext(policy):
        if not artifact_writes_must_encrypt(policy):
            # REQ-06: Phase 2 denial/telemetry events still emit plaintext metadata lines.
            if event_type not in _PHASE2_EVENT_TYPES_PLAINTEXT_OK:
                return

    log_path = resolve_audit_log_path()
    record: dict[str, Any] = {
        "timestamp": _utc_timestamp(),
        "event_type": event_type,
        "operation": operation,
        "result": result,
        "reason": reason,
    }
    extra = _scrub_metadata(metadata)
    if extra and policy is not None and policy.audit.include_reason_codes is False:
        extra = {k: v for k, v in extra.items() if k != "reason_code"}
    if extra:
        record["metadata"] = extra

    line_str = json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n"
    payload = (
        encrypt_audit_jsonl_line(line_str.encode("utf-8"), policy)
        if policy is not None and artifact_writes_must_encrypt(policy)
        else line_str.encode("utf-8")
    )
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    with _write_lock:
        try:
            with open(log_path, "ab") as fh:
                fh.write(payload)
        except OSError:
            return


def emit_phase2_artifact_encryption_event(
    policy: HardenedPolicy | None,
    *,
    operation: str,
    result: str,
    reason: str,
    event_subtype: str,
    path_hint: str | None = None,
) -> None:
    """Structured audit for artifact encryption outcomes (Phase 2 / REQ-06)."""
    meta: dict[str, Any] = {"event_subtype": event_subtype}
    if path_hint:
        meta["path_hint"] = path_hint
    emit_audit_record(
        policy,
        event_type="artifact_encryption",
        operation=operation,
        result=result,
        reason=reason,
        metadata=meta,
    )


def emit_phase2_filesystem_permissions_event(
    policy: HardenedPolicy | None,
    *,
    operation: str,
    result: str,
    reason: str,
    event_subtype: str,
) -> None:
    """Structured audit for POSIX permission hardening (Phase 2 / REQ-06)."""
    emit_audit_record(
        policy,
        event_type="filesystem_permissions",
        operation=operation,
        result=result,
        reason=reason,
        metadata={"event_subtype": event_subtype},
    )

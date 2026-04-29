"""Structured local audit events for security-relevant policy actions (REQ-06)."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
        if k in {"policy_path", "destination_host", "reason_code"} and isinstance(v, str):
            out[k] = v
        elif k in {"allowed"} and isinstance(v, bool):
            out[k] = v
    return out


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

    line = json.dumps(record, separators=(",", ":"), ensure_ascii=True) + "\n"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    with _write_lock:
        try:
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(line)
        except OSError:
            return

"""POSIX permission hardening for the local data directory (REQ-04, D-04)."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any

# Linux / macOS: owner-only data directory; private files
_DIR_MODE = 0o700
_FILE_MODE = 0o600


def apply_hardened_data_dir_permissions(data_dir: Path) -> None:
    """Set ``0o700`` on *data_dir* and ``0o600`` on files directly under it.

    Subdirectories directly under *data_dir* are set to ``0o700``. On Windows
    (``os.name == "nt"``) this is a no-op: NTFS permissions are not expressed
    as Unix octal modes and are not modified here.
    """
    if os.name == "nt":
        return
    resolved = data_dir.resolve()
    try:
        os.chmod(resolved, _DIR_MODE)
    except OSError:
        return
    try:
        for child in resolved.iterdir():
            try:
                if child.is_file():
                    os.chmod(child, _FILE_MODE)
                elif child.is_dir():
                    os.chmod(child, _DIR_MODE)
            except OSError:
                continue
    except OSError:
        return


def _mode_ok(path: Path, want_dir: bool) -> bool:
    try:
        st = path.stat()
    except OSError:
        return False
    mode = stat.S_IMODE(st.st_mode)
    return mode == (_DIR_MODE if want_dir else _FILE_MODE)


def verify_data_dir_permissions(data_dir: Path) -> dict[str, Any]:
    """Return a machine-parseable posture report for operators (REQ-04).

    Keys include ``keyword`` (``FS_PERMISSIONS_OK`` | ``FS_PERMISSIONS_WARN``
    | ``FS_PERMISSIONS_SKIP``), ``status`` (``ok`` | ``warn`` | ``skip``),
    and optional ``detail``, ``data_dir_mode_octal``, ``sample_issues``.
    """
    if os.name == "nt":
        return {
            "keyword": "FS_PERMISSIONS_SKIP",
            "status": "skip",
            "detail": "posix_chmod_not_applicable_windows",
        }

    resolved = data_dir.resolve()
    if not resolved.is_dir():
        return {
            "keyword": "FS_PERMISSIONS_WARN",
            "status": "warn",
            "detail": "data_dir_missing",
            "path_hint": resolved.name,
        }

    issues: list[str] = []
    if not _mode_ok(resolved, want_dir=True):
        issues.append(f"data_dir_mode_not_0700:{oct(stat.S_IMODE(resolved.stat().st_mode))}")

    try:
        for child in list(resolved.iterdir())[:50]:
            try:
                if child.is_file() and not _mode_ok(child, want_dir=False):
                    issues.append(
                        f"file_not_0600:{child.name}:{oct(stat.S_IMODE(child.stat().st_mode))}"
                    )
                elif child.is_dir() and not _mode_ok(child, want_dir=True):
                    issues.append(
                        f"subdir_not_0700:{child.name}:{oct(stat.S_IMODE(child.stat().st_mode))}"
                    )
            except OSError:
                continue
    except OSError:
        issues.append("cannot_iterate_data_dir")

    keyword = "FS_PERMISSIONS_OK" if not issues else "FS_PERMISSIONS_WARN"
    status = "ok" if not issues else "warn"
    out: dict[str, Any] = {
        "keyword": keyword,
        "status": status,
        "data_dir_mode_octal": oct(stat.S_IMODE(resolved.stat().st_mode)),
    }
    if issues:
        out["sample_issues"] = issues[:10]
    return out

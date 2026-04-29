"""Pure retention evaluation: candidate paths older than policy limits (REQ-05).

No side effects — deletion and SQLite maintenance happen in CLI ``cleanup-data --apply``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from .policy_schema import HardenedPolicy

_GRAPH_SIDE_CARS = ("-wal", "-shm", "-journal")


@dataclass(frozen=True)
class CleanupCandidate:
    """One artifact that exceeds configured retention."""

    path: Path
    sink: str
    reason: str
    age_days: float


def _file_age_days(path: Path) -> float:
    if not path.exists() or not path.is_file():
        return 0.0
    mtime = path.stat().st_mtime
    return (time.time() - mtime) / 86400.0


def evaluate_retention_candidates(
    policy: HardenedPolicy,
    data_dir: Path,
) -> list[CleanupCandidate]:
    """Return cleanup candidates under *data_dir* based on ``policy.retention``.

    *graph_derived*: applies to ``graph.db`` (mtime). Associated SQLite sidecar files
    are listed as separate candidates when the primary DB exceeds retention so operators
    can remove residuals; apply-order should delete sidecars after closing handles.
    """
    out: list[CleanupCandidate] = []
    ret = policy.retention

    # Audit log (default sink path under data dir; matches audit.resolve_audit_log_path layout)
    if ret.audit_log is not None:
        audit_file = data_dir / "policy_audit.jsonl"
        if audit_file.is_file():
            age = _file_age_days(audit_file)
            if age > ret.audit_log:
                out.append(
                    CleanupCandidate(
                        path=audit_file,
                        sink="audit_log",
                        reason=f"age {age:.1f}d > max {ret.audit_log}d",
                        age_days=age,
                    )
                )

    # Memory markdown artifacts
    if ret.memory_artifacts is not None:
        mem_dir = data_dir / "memory"
        if mem_dir.is_dir():
            for f in sorted(mem_dir.glob("*.md")):
                if not f.is_file():
                    continue
                age = _file_age_days(f)
                if age > ret.memory_artifacts:
                    out.append(
                        CleanupCandidate(
                            path=f,
                            sink="memory_artifacts",
                            reason=f"age {age:.1f}d > max {ret.memory_artifacts}d",
                            age_days=age,
                        )
                    )

    # Wiki outputs (same layout as ``wiki`` CLI: data_dir/wiki)
    if ret.wiki_outputs is not None:
        wiki_dir = data_dir / "wiki"
        if wiki_dir.is_dir():
            for f in sorted(wiki_dir.rglob("*.md")):
                if not f.is_file():
                    continue
                age = _file_age_days(f)
                if age > ret.wiki_outputs:
                    out.append(
                        CleanupCandidate(
                            path=f,
                            sink="wiki_outputs",
                            reason=f"age {age:.1f}d > max {ret.wiki_outputs}d",
                            age_days=age,
                        )
                    )

    # Graph SQLite bundle — coarse file-level retention (pragmatic local model D-03)
    if ret.graph_derived is not None:
        db = data_dir / "graph.db"
        if db.is_file():
            age = _file_age_days(db)
            if age > ret.graph_derived:
                out.append(
                    CleanupCandidate(
                        path=db,
                        sink="graph_derived",
                        reason=f"age {age:.1f}d > max {ret.graph_derived}d",
                        age_days=age,
                    )
                )
                for suffix in _GRAPH_SIDE_CARS:
                    side = Path(str(db) + suffix)
                    if side.is_file():
                        s_age = _file_age_days(side)
                        out.append(
                            CleanupCandidate(
                                path=side,
                                sink="graph_derived",
                                reason=f"sqlite sidecar (graph.db over retention); age {s_age:.1f}d",
                                age_days=s_age,
                            )
                        )

    return out

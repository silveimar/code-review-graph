"""Incremental graph update logic.

Detects changed files via git diff, re-parses only changed + impacted files,
and updates the graph accordingly. Also supports CLI invocation for hooks.
"""

from __future__ import annotations

import fnmatch
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional

from .graph import GraphStore
from .parser import CodeParser, file_hash

logger = logging.getLogger(__name__)

# Default ignore patterns (in addition to .gitignore)
DEFAULT_IGNORE_PATTERNS = [
    ".code-review-graph/**",
    "node_modules/**",
    ".git/**",
    "__pycache__/**",
    "*.pyc",
    ".venv/**",
    "venv/**",
    "dist/**",
    "build/**",
    ".next/**",
    "target/**",
    "*.min.js",
    "*.min.css",
    "*.map",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "*.db",
    "*.sqlite",
    "*.db-journal",
    "*.db-wal",
]


def find_repo_root(start: Path | None = None) -> Optional[Path]:
    """Walk up from start to find the nearest .git directory."""
    current = start or Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    if (current / ".git").exists():
        return current
    return None


def get_db_path(repo_root: Path) -> Path:
    """Determine the database path for a repository.

    Creates the ``.code-review-graph/`` directory and an inner ``.gitignore``
    (with ``*``) so generated files are never committed.  If a legacy
    ``.code-review-graph.db`` exists at the repo root the database is migrated
    into the new directory (WAL/SHM side-files are discarded).
    """
    crg_dir = repo_root / ".code-review-graph"
    new_db = crg_dir / "graph.db"

    # Ensure directory exists
    crg_dir.mkdir(exist_ok=True)

    # Auto-create .gitignore inside the directory (idempotent)
    inner_gitignore = crg_dir / ".gitignore"
    if not inner_gitignore.exists():
        inner_gitignore.write_text("*\n")

    # Migrate legacy database if present
    legacy_db = repo_root / ".code-review-graph.db"
    if legacy_db.exists() and not new_db.exists():
        legacy_db.rename(new_db)
    # Discard stale WAL/SHM side-files from the old location
    for suffix in ("-wal", "-shm", "-journal"):
        side = repo_root / f".code-review-graph.db{suffix}"
        if side.exists():
            side.unlink()

    return new_db


def _load_ignore_patterns(repo_root: Path) -> list[str]:
    """Load ignore patterns from .code-review-graphignore file."""
    patterns = list(DEFAULT_IGNORE_PATTERNS)
    ignore_file = repo_root / ".code-review-graphignore"
    if ignore_file.exists():
        for line in ignore_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


def _should_ignore(path: str, patterns: list[str]) -> bool:
    """Check if a path matches any ignore pattern."""
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def _is_binary(path: Path) -> bool:
    """Quick heuristic: check if file appears to be binary."""
    try:
        chunk = path.read_bytes()[:8192]
        return b"\x00" in chunk
    except (OSError, PermissionError):
        return True


def get_changed_files(repo_root: Path, base: str = "HEAD~1") -> list[str]:
    """Get list of changed files via git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        if result.returncode != 0:
            # Fallback: try diff against empty tree (initial commit)
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                cwd=str(repo_root),
            )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        return files
    except FileNotFoundError:
        return []


def get_staged_and_unstaged(repo_root: Path) -> list[str]:
    """Get all modified files (staged + unstaged + untracked)."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        files = []
        for line in result.stdout.splitlines():
            if len(line) > 3:
                files.append(line[3:].strip())
        return files
    except FileNotFoundError:
        return []


def get_all_tracked_files(repo_root: Path) -> list[str]:
    """Get all files tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            cwd=str(repo_root),
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except FileNotFoundError:
        return []


def collect_all_files(repo_root: Path) -> list[str]:
    """Collect all parseable files in the repo, respecting ignore patterns."""
    ignore_patterns = _load_ignore_patterns(repo_root)
    parser = CodeParser()
    files = []

    # Prefer git ls-files for tracked files
    tracked = get_all_tracked_files(repo_root)
    if tracked:
        candidates = tracked
    else:
        # Fallback: walk directory
        candidates = [
            str(p.relative_to(repo_root))
            for p in repo_root.rglob("*")
            if p.is_file()
        ]

    for rel_path in candidates:
        if _should_ignore(rel_path, ignore_patterns):
            continue
        full_path = repo_root / rel_path
        if not full_path.is_file():
            continue
        if parser.detect_language(full_path) is None:
            continue
        if _is_binary(full_path):
            continue
        files.append(rel_path)

    return files


def find_dependents(store: GraphStore, file_path: str) -> list[str]:
    """Find files that import from or depend on the given file.

    Looks at IMPORTS_FROM edges where target matches the file path.
    """
    dependents = set()
    # Find edges where someone imports from this file
    edges = store.get_edges_by_target(file_path)
    for e in edges:
        if e.kind == "IMPORTS_FROM":
            # The source is a file path (for IMPORTS_FROM edges)
            dependents.add(e.file_path)

    # Also check for DEPENDS_ON edges
    nodes = store.get_nodes_by_file(file_path)
    for node in nodes:
        for e in store.get_edges_by_target(node.qualified_name):
            if e.kind in ("CALLS", "IMPORTS_FROM", "INHERITS", "IMPLEMENTS"):
                dependents.add(e.file_path)

    dependents.discard(file_path)
    return list(dependents)


def full_build(repo_root: Path, store: GraphStore) -> dict:
    """Full rebuild of the entire graph."""
    parser = CodeParser()
    _load_ignore_patterns(repo_root)
    files = collect_all_files(repo_root)

    total_nodes = 0
    total_edges = 0
    errors = []

    for rel_path in files:
        full_path = repo_root / rel_path
        try:
            fhash = file_hash(full_path)
            nodes, edges = parser.parse_file(full_path)
            store.store_file_nodes_edges(str(full_path), nodes, edges, fhash)
            total_nodes += len(nodes)
            total_edges += len(edges)
        except Exception as e:
            errors.append({"file": rel_path, "error": str(e)})

    store.set_metadata("last_updated", time.strftime("%Y-%m-%dT%H:%M:%S"))
    store.set_metadata("last_build_type", "full")
    store.commit()

    return {
        "files_parsed": len(files),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "errors": errors,
    }


def incremental_update(
    repo_root: Path,
    store: GraphStore,
    base: str = "HEAD~1",
    changed_files: list[str] | None = None,
) -> dict:
    """Incremental update: re-parse changed + dependent files only."""
    parser = CodeParser()
    ignore_patterns = _load_ignore_patterns(repo_root)

    # Determine changed files
    if changed_files is None:
        changed_files = get_changed_files(repo_root, base)

    if not changed_files:
        return {
            "files_updated": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "changed_files": [],
            "dependent_files": [],
        }

    # Find dependent files (files that import from changed files)
    dependent_files: set[str] = set()
    for rel_path in changed_files:
        full_path = str(repo_root / rel_path)
        deps = find_dependents(store, full_path)
        for d in deps:
            # Convert back to relative path if needed
            try:
                dependent_files.add(str(Path(d).relative_to(repo_root)))
            except ValueError:
                dependent_files.add(d)

    # Combine changed + dependent
    all_files = set(changed_files) | dependent_files

    total_nodes = 0
    total_edges = 0
    errors = []

    for rel_path in all_files:
        if _should_ignore(rel_path, ignore_patterns):
            continue
        full_path = repo_root / rel_path
        if not full_path.is_file():
            # File was deleted
            store.remove_file_data(str(full_path))
            continue
        if parser.detect_language(full_path) is None:
            continue

        try:
            fhash = file_hash(full_path)
            # Check if file actually changed
            existing_nodes = store.get_nodes_by_file(str(full_path))
            if existing_nodes and existing_nodes[0].extra.get("file_hash") == fhash:
                # Skip unchanged files (hash match)
                continue

            nodes, edges = parser.parse_file(full_path)
            store.store_file_nodes_edges(str(full_path), nodes, edges, fhash)
            total_nodes += len(nodes)
            total_edges += len(edges)
        except Exception as e:
            errors.append({"file": rel_path, "error": str(e)})

    store.set_metadata("last_updated", time.strftime("%Y-%m-%dT%H:%M:%S"))
    store.set_metadata("last_build_type", "incremental")
    store.commit()

    return {
        "files_updated": len(all_files),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "changed_files": list(changed_files),
        "dependent_files": list(dependent_files),
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Watch mode
# ---------------------------------------------------------------------------


_DEBOUNCE_SECONDS = 0.3


def watch(repo_root: Path, store: GraphStore) -> None:
    """Watch for file changes and auto-update the graph.

    Uses a 300ms debounce to batch rapid-fire saves into a single update.
    """
    import threading

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    parser = CodeParser()
    ignore_patterns = _load_ignore_patterns(repo_root)

    class GraphUpdateHandler(FileSystemEventHandler):
        def __init__(self):
            self._pending: set[str] = set()
            self._lock = threading.Lock()
            self._timer: threading.Timer | None = None

        def _should_handle(self, path: str) -> bool:
            try:
                rel = str(Path(path).relative_to(repo_root))
            except ValueError:
                return False
            if _should_ignore(rel, ignore_patterns):
                return False
            if parser.detect_language(Path(path)) is None:
                return False
            return True

        def on_modified(self, event):
            if event.is_directory:
                return
            if self._should_handle(event.src_path):
                self._schedule(event.src_path)

        def on_created(self, event):
            if event.is_directory:
                return
            if self._should_handle(event.src_path):
                self._schedule(event.src_path)

        def on_deleted(self, event):
            if event.is_directory:
                return
            store.remove_file_data(event.src_path)
            store.commit()
            rel = str(Path(event.src_path).relative_to(repo_root))
            logger.info("Removed: %s", rel)

        def _schedule(self, abs_path: str):
            """Add file to pending set and reset the debounce timer."""
            with self._lock:
                self._pending.add(abs_path)
                if self._timer is not None:
                    self._timer.cancel()
                self._timer = threading.Timer(
                    _DEBOUNCE_SECONDS, self._flush
                )
                self._timer.start()

        def _flush(self):
            """Process all pending files after the debounce window."""
            with self._lock:
                paths = list(self._pending)
                self._pending.clear()
                self._timer = None

            for abs_path in paths:
                self._update_file(abs_path)

        def _update_file(self, abs_path: str):
            path = Path(abs_path)
            if not path.is_file():
                return
            if _is_binary(path):
                return
            try:
                fhash = file_hash(path)
                nodes, edges = parser.parse_file(path)
                store.store_file_nodes_edges(abs_path, nodes, edges, fhash)
                store.set_metadata(
                    "last_updated", time.strftime("%Y-%m-%dT%H:%M:%S")
                )
                store.commit()
                rel = str(path.relative_to(repo_root))
                logger.info(
                    "Updated: %s (%d nodes, %d edges)",
                    rel, len(nodes), len(edges),
                )
            except Exception as e:
                logger.error("Error updating %s: %s", abs_path, e)

    handler = GraphUpdateHandler()
    observer = Observer()
    observer.schedule(handler, str(repo_root), recursive=True)
    observer.start()

    logger.info("Watching %s for changes... (Ctrl+C to stop)", repo_root)
    try:
        import time as _time
        while True:
            _time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logger.info("Watch stopped.")


# ---------------------------------------------------------------------------
# CLI entry point for hooks
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point: python -m server.incremental update [--full] [--base BASE] [--watch]"""
    import argparse

    ap = argparse.ArgumentParser(description="Code Review Graph - incremental updater")
    ap.add_argument(
        "action", choices=["update", "build", "status", "watch"],
        help="Action to perform",
    )
    ap.add_argument("--full", action="store_true", help="Force full rebuild")
    ap.add_argument("--base", default="HEAD~1", help="Git diff base (default: HEAD~1)")
    ap.add_argument("--repo", default=None, help="Repository root (auto-detected)")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    repo_root = Path(args.repo) if args.repo else find_repo_root()
    if not repo_root:
        logger.error("Not in a git repository")
        return

    db_path = get_db_path(repo_root)
    store = GraphStore(db_path)

    try:
        if args.action == "status":
            stats = store.get_stats()
            print(f"Nodes: {stats.total_nodes}")
            print(f"Edges: {stats.total_edges}")
            print(f"Files: {stats.files_count}")
            print(f"Languages: {', '.join(stats.languages)}")
            print(f"Last updated: {stats.last_updated or 'never'}")
        elif args.action == "build" or args.full:
            result = full_build(repo_root, store)
            print(f"Full build: {result['files_parsed']} files, "
                  f"{result['total_nodes']} nodes, {result['total_edges']} edges")
            if result["errors"]:
                print(f"Errors: {len(result['errors'])}")
        elif args.action == "watch":
            watch(repo_root, store)
        else:
            result = incremental_update(repo_root, store, base=args.base)
            print(f"Incremental: {result['files_updated']} files updated, "
                  f"{result['total_nodes']} nodes, {result['total_edges']} edges")
    finally:
        store.close()


if __name__ == "__main__":
    main()

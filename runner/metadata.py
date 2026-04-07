from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path


def make_run_id(run_name: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{run_name}_{timestamp}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def collect_git_metadata(root: Path) -> dict:
    if not (root / ".git").exists():
        return {
            "is_git_repo": False,
            "branch": None,
            "commit_hash": None,
            "is_dirty": None,
        }

    return {
        "is_git_repo": True,
        "branch": _git_or_none(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit_hash": _git_or_none(root, ["rev-parse", "HEAD"]),
        "is_dirty": _git_is_dirty(root),
    }


def _git_or_none(root: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None
    except subprocess.CalledProcessError:
        return None


def _git_is_dirty(root: Path) -> bool | None:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return None

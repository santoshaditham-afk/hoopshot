#!/usr/bin/env python3
"""
record_merge.py — Record a merge checkpoint and PR approval to SQLite.

Called by CI on every push to main. Can also be run locally for testing.

Environment variables (all optional; falls back to git commands / empty strings):
    GITHUB_SHA    — full commit SHA
    PR_NUMBER     — PR number that was merged
    PR_TITLE      — PR title
    PR_BODY       — PR description / summary
    PR_AUTHOR     — GitHub login of PR author
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Resolve project root (two levels up from this script) ──────────────────
ROOT = Path(__file__).parent.parent
BACKEND_DIR = ROOT / "backend"

# Add backend to sys.path so we can import the app package directly
sys.path.insert(0, str(BACKEND_DIR))

# Change working directory to backend so SQLAlchemy relative paths resolve
os.chdir(BACKEND_DIR)

from sqlalchemy.orm import Session  # noqa: E402

# Import models (this also triggers Base / AuditBase registration)
from app.database import engine, Base  # noqa: E402
from app.audit_db import audit_engine, AuditBase  # noqa: E402
from app.models import MergeCheckpoint  # noqa: E402
from app.audit_models import PRApproval  # noqa: E402

# Ensure tables exist
Base.metadata.create_all(bind=engine)
AuditBase.metadata.create_all(bind=audit_engine)


# ── Git helpers ─────────────────────────────────────────────────────────────

def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def compute_content_hash() -> str:
    """SHA256 over all git-tracked files (sorted by relative path)."""
    tracked = git("ls-files").splitlines()
    h = hashlib.sha256()
    for rel in sorted(tracked):
        p = ROOT / rel
        try:
            h.update(rel.encode())
            h.update(p.read_bytes())
        except OSError:
            pass
    return h.hexdigest()


def compute_artifact_hash() -> str:
    """SHA256 over files changed between HEAD~1 and HEAD."""
    changed = git("diff", "--name-only", "HEAD~1", "HEAD").splitlines()
    h = hashlib.sha256()
    for rel in sorted(changed):
        p = ROOT / rel
        try:
            h.update(rel.encode())
            h.update(p.read_bytes())
        except OSError:
            pass
    return h.hexdigest()


# ── Main ────────────────────────────────────────────────────────────────────

def main() -> None:
    commit_sha = os.environ.get("GITHUB_SHA") or git("rev-parse", "HEAD") or "unknown"
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "main"
    author = git("log", "-1", "--format=%an <%ae>") or "unknown"
    message = git("log", "-1", "--format=%s") or ""

    pr_number_raw = os.environ.get("PR_NUMBER", "")
    pr_number = int(pr_number_raw) if pr_number_raw.isdigit() else None
    pr_title = os.environ.get("PR_TITLE", "")
    pr_body = os.environ.get("PR_BODY", "")
    pr_author = os.environ.get("PR_AUTHOR", author)

    print("Computing content hash (all tracked files)…")
    content_hash = compute_content_hash()

    print("Computing artifact hash (changed files)…")
    artifact_hash = compute_artifact_hash()

    now = datetime.now(timezone.utc)

    # Write MergeCheckpoint → hoopshot.db
    with Session(engine) as session:
        existing = session.query(MergeCheckpoint).filter_by(commit_sha=commit_sha).first()
        if existing:
            print(f"Checkpoint already recorded for {commit_sha[:12]} — skipping duplicate.")
        else:
            checkpoint = MergeCheckpoint(
                commit_sha=commit_sha,
                content_hash=content_hash,
                branch=branch,
                author=author,
                message=message,
                merged_at=now,
            )
            session.add(checkpoint)
            session.commit()
            print(f"MergeCheckpoint written  → hoopshot.db  (sha={commit_sha[:12]})")

    # Write PRApproval → pr_audit.db
    with Session(audit_engine) as session:
        approval = PRApproval(
            pr_number=pr_number,
            pr_title=pr_title,
            pr_author=pr_author,
            artifact_hash=artifact_hash,
            summary=pr_body,
            approved_at=now,
        )
        session.add(approval)
        session.commit()
        print(f"PRApproval written       → pr_audit.db   (pr=#{pr_number}, artifact={artifact_hash[:12]})")

    print("\n── Summary ──────────────────────────────────────────")
    print(f"  commit_sha   : {commit_sha[:12]}")
    print(f"  content_hash : {content_hash[:12]}")
    print(f"  artifact_hash: {artifact_hash[:12]}")
    print(f"  branch       : {branch}")
    print(f"  author       : {author}")
    print(f"  pr_number    : {pr_number}")
    print(f"  pr_title     : {pr_title or '(none)'}")
    print("─────────────────────────────────────────────────────")


if __name__ == "__main__":
    main()

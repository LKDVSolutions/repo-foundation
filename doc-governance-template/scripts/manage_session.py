#!/usr/bin/env python3
"""Create and resume session envelopes for agent handoff continuity."""

from __future__ import annotations

import argparse
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml
from filelock import FileLock, Timeout

try:
    from governance_logger import get_governance_logger
except ImportError:  # pragma: no cover - used when imported as scripts.manage_session
    from scripts.governance_logger import get_governance_logger

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SESSIONS_DIR = REPO_ROOT / "docs" / "history"
SESSION_LOCK = REPO_ROOT / "docs" / "history" / "SESSION_ENVELOPES.lock"
LOCK_TIMEOUT = 30
LOGGER = get_governance_logger("manage_session.py")


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _session_id() -> str:
    now = datetime.now(tz=timezone.utc)
    return f"session-{now.strftime('%Y%m%d-%H%M')}-{uuid.uuid4().hex[:6]}"


def _session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"SESSION_{session_id}.md"


def _git_diff_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()[:12]


def _render_envelope(
    session_id: str,
    parent_task_id: str,
    active_files: list[str],
    checkpoint_summary: str,
    git_diff_sha: str,
    resume_target_file: str,
    resume_target_line: int,
) -> str:
    frontmatter = {
        "doc_id": f"SESSION_{session_id}",
        "doc_class": "active",
        "authority_kind": "current_config",
        "title": f"Session Envelope {session_id}",
        "primary_audience": "agents",
        "task_entry_for": [],
        "system_owner": "documentation-governance",
        "doc_owner": "system-wide",
        "updated_by": "auto",
        "authoritative_for": [
            "session continuity checkpoint",
            "agent resume context",
        ],
        "source_inputs": ["scripts/manage_session.py"],
        "refresh_policy": "auto",
        "verification_level": "repo_derived",
        "status": "active",
        "depends_on": ["AGENT_WORKFLOW_md"],
    }

    body_lines = [
        "# Session Envelope",
        "",
        "## Session Metadata",
        f"- session_id: {session_id}",
        f"- parent_task_id: {parent_task_id}",
        f"- git_diff_sha: {git_diff_sha}",
        f"- created_at: {_now_iso()}",
        "",
        "## Active Scope",
        "- active_files:",
    ]
    if active_files:
        for item in active_files:
            body_lines.append(f"  - {item}")
    else:
        body_lines.append("  - none")

    body_lines.extend(
        [
            "",
            "## Checkpoint",
            f"- checkpoint_summary: {checkpoint_summary}",
            f"- resume_target_file: {resume_target_file}",
            f"- resume_target_line: {resume_target_line}",
        ]
    )

    fm_text = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    return f"---\n{fm_text}\n---\n" + "\n".join(body_lines) + "\n"


def create_session(
    parent_task_id: str,
    active_files: list[str],
    checkpoint_summary: str,
    git_diff_sha: str | None,
    resume_target_file: str,
    resume_target_line: int,
) -> int:
    session_id = _session_id()
    path = _session_path(session_id)
    diff_sha = git_diff_sha or _git_diff_sha()

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with FileLock(str(SESSION_LOCK), timeout=LOCK_TIMEOUT):
            if path.exists():
                LOGGER.log("ERROR", "session_create_conflict", f"Session envelope already exists: {path.name}", doc_id="SESSION_ENVELOPE")
                return 1
            content = _render_envelope(
                session_id=session_id,
                parent_task_id=parent_task_id,
                active_files=active_files,
                checkpoint_summary=checkpoint_summary,
                git_diff_sha=diff_sha,
                resume_target_file=resume_target_file,
                resume_target_line=resume_target_line,
            )
            path.write_text(content, encoding="utf-8")
    except Timeout:
        LOGGER.log("ERROR", "session_create_lock_timeout", f"Could not acquire lock after {LOCK_TIMEOUT}s", doc_id="SESSION_ENVELOPE")
        return 2

    LOGGER.log("INFO", "session_created", f"Created session envelope {path.name}", doc_id="SESSION_ENVELOPE")
    return 0


def _extract_checkpoint(content: str) -> tuple[str, int, str]:
    resume_file = ""
    resume_line = 1
    summary = ""
    for line in content.splitlines():
        if line.startswith("- resume_target_file:"):
            resume_file = line.split(":", 1)[1].strip()
        elif line.startswith("- resume_target_line:"):
            try:
                resume_line = int(line.split(":", 1)[1].strip())
            except ValueError:
                resume_line = 1
        elif line.startswith("- checkpoint_summary:"):
            summary = line.split(":", 1)[1].strip()
    return resume_file, resume_line, summary


def resume_session(session_id: str) -> int:
    path = _session_path(session_id)
    try:
        with FileLock(str(SESSION_LOCK), timeout=LOCK_TIMEOUT):
            if not path.exists():
                LOGGER.log("ERROR", "session_resume_missing", f"Session envelope not found: {path.name}", doc_id="SESSION_ENVELOPE")
                return 1
            content = path.read_text(encoding="utf-8")
    except Timeout:
        LOGGER.log("ERROR", "session_resume_lock_timeout", f"Could not acquire lock after {LOCK_TIMEOUT}s", doc_id="SESSION_ENVELOPE")
        return 2

    resume_file, resume_line, summary = _extract_checkpoint(content)
    if not resume_file:
        LOGGER.log("ERROR", "session_resume_invalid", f"Session envelope missing resume target: {path.name}", doc_id="SESSION_ENVELOPE")
        return 1

    LOGGER.log(
        "INFO",
        "session_resume_ready",
        f"Resume at {resume_file}:{resume_line}. Summary: {summary}",
        doc_id="SESSION_ENVELOPE",
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage agent session envelopes.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new session envelope")
    create_parser.add_argument("--parent-task-id", required=True)
    create_parser.add_argument("--active-file", action="append", default=[])
    create_parser.add_argument("--checkpoint-summary", required=True)
    create_parser.add_argument("--git-diff-sha", default=None)
    create_parser.add_argument("--resume-target-file", required=True)
    create_parser.add_argument("--resume-target-line", type=int, default=1)

    resume_parser = subparsers.add_parser("resume", help="Resume from an existing session envelope")
    resume_parser.add_argument("--session-id", required=True)

    args = parser.parse_args()

    if args.command == "create":
        return create_session(
            parent_task_id=args.parent_task_id,
            active_files=args.active_file,
            checkpoint_summary=args.checkpoint_summary,
            git_diff_sha=args.git_diff_sha,
            resume_target_file=args.resume_target_file,
            resume_target_line=args.resume_target_line,
        )

    if args.command == "resume":
        return resume_session(session_id=args.session_id)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

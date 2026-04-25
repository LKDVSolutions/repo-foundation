#!/usr/bin/env python3
"""Structured governance audit logger."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from filelock import FileLock

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
AUDIT_TRAIL_PATH = REPO_ROOT / ".runtime" / "AGENT_AUDIT_TRAIL.jsonl"
LOCK_TIMEOUT_SECONDS = 30


class GovernanceLogger:
    """Append-only JSON logger for governance scripts."""

    def __init__(self, script: str, audit_path: Path = AUDIT_TRAIL_PATH) -> None:
        self.script = script
        self.audit_path = audit_path
        self.lock_path = audit_path.with_suffix(".jsonl.lock")

    def log(self, level: str, event: str, message: str, doc_id: str = "none") -> None:
        """Write one structured event record to the runtime audit trail."""
        record = {
            "timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": level,
            "script": self.script,
            "event": event,
            "doc_id": doc_id,
            "message": message,
        }

        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(str(self.lock_path), timeout=LOCK_TIMEOUT_SECONDS):
            with self.audit_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def get_governance_logger(script: str) -> GovernanceLogger:
    """Return a configured logger instance for a script name."""
    return GovernanceLogger(script=script)

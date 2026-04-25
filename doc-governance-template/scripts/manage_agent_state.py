#!/usr/bin/env python3
"""Programmatically transition agent state in docs/history/AGENT_STATE.md."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import yaml
from filelock import FileLock, Timeout

try:
    from governance_logger import get_governance_logger
except ImportError:  # pragma: no cover
    from scripts.governance_logger import get_governance_logger

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_STATE_PATH = REPO_ROOT / "docs" / "history" / "AGENT_STATE.md"
LOCK_PATH = AGENT_STATE_PATH.with_suffix(".lock")
LOCK_TIMEOUT = 30
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LOGGER = get_governance_logger("manage_agent_state.py")


def _parse_document(content: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = content[match.end():]
    return frontmatter, body


def _render_document(frontmatter: dict, body: str) -> str:
    fm_text = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    return f"---\n{fm_text}\n---\n" + body


def update_agent_state(state_change: str, new_blocker: str | None = None) -> bool:
    if not AGENT_STATE_PATH.exists():
        LOGGER.log("ERROR", "state_file_missing", "AGENT_STATE.md not found", doc_id="AGENT_STATE")
        return False

    original = AGENT_STATE_PATH.read_text(encoding="utf-8")
    frontmatter, body = _parse_document(original)
    
    # Initialize state object if missing
    if "agent_state" not in frontmatter:
        frontmatter["agent_state"] = {"status": "Unknown", "blockers": []}
    
    # Update frontmatter
    frontmatter["agent_state"]["status"] = state_change
    if new_blocker:
        if new_blocker not in frontmatter["agent_state"]["blockers"]:
            frontmatter["agent_state"]["blockers"].append(new_blocker)
    
    frontmatter["last_verified"] = str(date.today())

    # Update body for human readability
    today_str = str(date.today())
    blockers_list = frontmatter["agent_state"]["blockers"]
    blockers_text = "\n".join([f"- {b}" for b in blockers_list]) if blockers_list else "- None"
    
    new_body = f"""
# Agent State

**Authoritative state is in the YAML frontmatter above.**

This document provides a trace of the current agent's operational status. The `manage_agent_state.py` script maintains the frontmatter keys.

## Active Status
- **Current Status**: {state_change}
- **Last Updated**: {today_str}

## Blockers
{blockers_text}
"""

    updated = _render_document(frontmatter, new_body)
    if updated == original:
        LOGGER.log("INFO", "state_noop", "No changes applied to AGENT_STATE.md", doc_id="AGENT_STATE")
        return True

    AGENT_STATE_PATH.write_text(updated, encoding="utf-8")
    LOGGER.log("INFO", "state_updated", f"Updated AGENT_STATE.md state={state_change} blocker={new_blocker}", doc_id="AGENT_STATE")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="Idle", help="New state")
    parser.add_argument("--blocker", default=None, help="New blocker (optional)")
    args = parser.parse_args()

    print("=== manage_agent_state.py ===")
    try:
        with FileLock(str(LOCK_PATH), timeout=LOCK_TIMEOUT):
            ok = update_agent_state(args.state, args.blocker)
    except Timeout:
        LOGGER.log("ERROR", "state_lock_timeout", f"Lock not acquired after {LOCK_TIMEOUT}s", doc_id="AGENT_STATE")
        return 2

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

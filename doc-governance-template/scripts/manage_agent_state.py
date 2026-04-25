#!/usr/bin/env python3
"""Programmatically transition agent state in docs/history/AGENT_STATE.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml
from filelock import FileLock, Timeout

try:
    from governance_logger import get_governance_logger
except ImportError:  # pragma: no cover - used when imported as scripts.manage_agent_state
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
    if not frontmatter:
        return body
    fm_text = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    return f"---\n{fm_text}\n---\n" + body


def _update_status(body: str, state_change: str) -> str:
    pattern = re.compile(r"^(\s*-\s*\*\*Status\*\*:\s*).*$", re.MULTILINE)
    if pattern.search(body):
        return pattern.sub(rf"\1{state_change}", body, count=1)

    lines = body.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "## Current Task":
            lines.insert(idx + 1, f"- **Status**: {state_change}")
            return "\n".join(lines) + ("\n" if body.endswith("\n") else "")

    return body.rstrip() + f"\n\n## Current Task\n- **Status**: {state_change}\n"


def _update_blocker(body: str, new_blocker: str) -> str:
    lines = body.splitlines()
    section_start = -1
    section_end = len(lines)

    for idx, line in enumerate(lines):
        if line.strip() == "## Blockers / Issues":
            section_start = idx
            break

    if section_start == -1:
        return body.rstrip() + f"\n\n## Blockers / Issues\n- [ ] {new_blocker}\n"

    for idx in range(section_start + 1, len(lines)):
        if lines[idx].startswith("## "):
            section_end = idx
            break

    checkbox_pattern = re.compile(r"^(\s*-\s*\[[ xX]\]\s*).*$")
    for idx in range(section_start + 1, section_end):
        if checkbox_pattern.match(lines[idx]):
            lines[idx] = f"- [ ] {new_blocker}"
            return "\n".join(lines) + ("\n" if body.endswith("\n") else "")

    lines.insert(section_start + 1, f"- [ ] {new_blocker}")
    return "\n".join(lines) + ("\n" if body.endswith("\n") else "")


def update_agent_state(state_change: str, new_blocker: str | None = None) -> bool:
    if not AGENT_STATE_PATH.exists():
        LOGGER.log("ERROR", "state_file_missing", "AGENT_STATE.md not found", doc_id="AGENT_STATE")
        return False

    original = AGENT_STATE_PATH.read_text(encoding="utf-8")
    frontmatter, body = _parse_document(original)
    updated_body = _update_status(body, state_change)
    if new_blocker:
        updated_body = _update_blocker(updated_body, new_blocker)

    updated = _render_document(frontmatter, updated_body)
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

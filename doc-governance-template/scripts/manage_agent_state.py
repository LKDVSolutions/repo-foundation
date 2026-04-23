#!/usr/bin/env python3
"""Programmatically transition agent states, update blockers, and rotate task queues in AGENT_STATE.md."""

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_STATE_PATH = REPO_ROOT / "docs" / "history" / "AGENT_STATE.md"


def update_agent_state(state_change: str, new_blocker: str | None = None) -> None:
    if not AGENT_STATE_PATH.exists():
        print("AGENT_STATE.md not found.")
        return

    lines = AGENT_STATE_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    updated = []
    for line in lines:
        if line.startswith("**Current State**:"):
            line = f"**Current State**: {state_change}\n"
        elif new_blocker and line.startswith("**Blockers**:"):
            line = f"**Blockers**: {new_blocker}\n"
        updated.append(line)

    AGENT_STATE_PATH.write_text("".join(updated), encoding="utf-8")
    print(f"Updated AGENT_STATE.md. State: {state_change}, Blocker: {new_blocker}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="Idle", help="New state")
    parser.add_argument("--blocker", default=None, help="New blocker (optional)")
    args = parser.parse_args()

    print("=== manage_agent_state.py ===")
    update_agent_state(args.state, args.blocker)


if __name__ == "__main__":
    main()

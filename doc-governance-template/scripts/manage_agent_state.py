#!/usr/bin/env python3
"""Programmatically transition agent states, update blockers, and rotate task queues in AGENT_STATE.md."""

import re
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_STATE_PATH = REPO_ROOT / "docs" / "history" / "AGENT_STATE.md"

def update_agent_state(state_change: str, new_blocker: str = None):
    if not AGENT_STATE_PATH.exists():
        print("AGENT_STATE.md not found.")
        return
        
    with open(AGENT_STATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    content = re.sub(r'(\*\*Current State\*\*:\s*).*', r'\g<1>' + state_change, content)
    
    if new_blocker:
        content = re.sub(r'(\*\*Blockers\*\*:\s*).*', r'\g<1>' + new_blocker, content)
        
    with open(AGENT_STATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Updated AGENT_STATE.md. State: {state_change}, Blocker: {new_blocker}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="Idle", help="New state")
    parser.add_argument("--blocker", default="None", help="New blocker")
    args = parser.parse_args()
    
    print("=== manage_agent_state.py ===")
    update_agent_state(args.state, args.blocker)

if __name__ == "__main__":
    main()

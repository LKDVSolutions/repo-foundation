#!/usr/bin/env python3
import sys
import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

def request_human(message):
    needs_attention_file = REPO_ROOT / "docs" / "plans" / "NEEDS_ATTENTION.md"
    
    # Ensure the file exists
    if not needs_attention_file.exists():
        needs_attention_file.parent.mkdir(parents=True, exist_ok=True)
        needs_attention_file.write_text("# Needs Attention\n\n", encoding='utf-8')
        
    # Get git diff
    try:
        git_diff = subprocess.run(["git", "diff"], capture_output=True, text=True).stdout
    except Exception:
        git_diff = "N/A"
        
    payload = {
        "message": message,
        "git_diff": git_diff[:2000] + ("..." if len(git_diff) > 2000 else ""),
        "agent_memory": "Check .agent_context.md"
    }
    
    payload_str = json.dumps(payload, indent=2)
    
    with open(needs_attention_file, "a", encoding='utf-8') as f:
        f.write(f"- **AGENT REQUEST**: {message}\n```json\n{payload_str}\n```\n")
        
    sys.stdout.write('\a')
    sys.stdout.flush()
    
    print(f"\n[!] Human Attention Requested: {message}")
    print(f"Logged to {needs_attention_file}.")
    print("Halting agent execution loop.")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/request_human.py \"Your message here\"")
        sys.exit(1)
        
    request_human(sys.argv[1])

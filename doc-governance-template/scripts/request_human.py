#!/usr/bin/env python3
import sys
import os
from pathlib import Path

def request_human(message):
    needs_attention_file = Path("docs/plans/NEEDS_ATTENTION.md")
    
    # Ensure the file exists
    if not needs_attention_file.exists():
        needs_attention_file.parent.mkdir(parents=True, exist_ok=True)
        needs_attention_file.write_text("# Needs Attention\n\n", encoding='utf-8')
        
    with open(needs_attention_file, "a", encoding='utf-8') as f:
        f.write(f"- **AGENT REQUEST**: {message}\n")
        
    # Ring terminal bell
    sys.stdout.write('\a')
    sys.stdout.flush()
    
    print(f"\n[!] Human Attention Requested: {message}")
    print(f"Logged to {needs_attention_file}.")
    print("Halting agent execution loop.")
    sys.exit(1)  # Non-zero exit to halt agent workflows

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/request_human.py \"Your message here\"")
        sys.exit(1)
        
    request_human(sys.argv[1])
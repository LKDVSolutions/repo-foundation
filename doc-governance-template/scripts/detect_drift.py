#!/usr/bin/env python3
"""Auto-Drift Detection (Cron Job)

Periodically compares `current_config` (e.g., docker-compose.yml) 
against expected blueprints to automatically flag drift, and draft PRs.
"""

import os
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
IDEA_INBOX = REPO_ROOT / "docs" / "plans" / "IDEA_INBOX.md"

def log_drift(message: str):
    """Appends a drift notification to the IDEA_INBOX."""
    if not IDEA_INBOX.exists():
        return
    
    content = IDEA_INBOX.read_text(encoding="utf-8")
    entry = f"\n## Automated Drift Report\n**Detected:** {message}\n"
    
    if entry not in content:
        with IDEA_INBOX.open("a", encoding="utf-8") as f:
            f.write(entry)
        print(f"Logged drift: {message}")

def draft_pr_for_drift(message: str):
    """Drafts a GitHub PR for the detected drift using gh CLI."""
    try:
        subprocess.run(
            ["gh", "issue", "create", "--title", "Drift Detected", "--body", message],
            check=True,
            capture_output=True
        )
        print("Created GitHub issue for drift.")
    except Exception as e:
        print(f"Failed to create GitHub issue: {e}")

def check_docker_compose_drift():
    compose_file = REPO_ROOT / "docker-compose.yml"
    blueprint_file = REPO_ROOT / "docs" / "reference" / "architecture.md"
    
    if compose_file.exists() and blueprint_file.exists():
        compose_content = compose_file.read_text()
        blueprint_content = blueprint_file.read_text()
        
        # Naive comparison
        if "services:" in compose_content and "services:" not in blueprint_content:
            msg = "docker-compose.yml has services not documented in architecture.md"
            log_drift(msg)
            draft_pr_for_drift(msg)

def main():
    print("Running Auto-Drift Detection...")
    check_docker_compose_drift()
    print("Auto-Drift Detection complete.")

if __name__ == "__main__":
    main()

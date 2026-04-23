#!/usr/bin/env python3
"""CLI to automatically repair missing frontmatter, format YAML strings, and append missing standard headings."""

import os
import sys
import yaml
from pathlib import Path

def fix_markdown_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    fixed = False
    
    # 1. Ensure frontmatter
    if not content.startswith("---\n"):
        frontmatter = "---\ntitle: Auto-generated Title\nstatus: active\n---\n"
        content = frontmatter + content
        fixed = True
    
    # 2. Append standard heading if missing
    if "## Governance" not in content and "## Introduction" not in content:
        content = content.rstrip() + "\n\n## Governance\n\nThis section was auto-added by auto_fix.py.\n"
        fixed = True
        
    if fixed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed: {path.name}")
        return True
    return False

def main():
    print("=== auto_fix.py ===")
    repo_root = Path(__file__).resolve().parent.parent
    docs_dir = repo_root / "docs"
    
    fixes = 0
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                if fix_markdown_file(Path(root) / file):
                    fixes += 1
                    
    print(f"Total files fixed: {fixes}")

if __name__ == "__main__":
    main()

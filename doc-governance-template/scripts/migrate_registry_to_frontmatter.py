#!/usr/bin/env python3
"""Migrate DOC_REGISTRY.yaml metadata to individual Markdown file frontmatter."""

import sys
import yaml
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"

# Regex to detect existing YAML frontmatter
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def migrate_registry():
    if not REGISTRY_PATH.exists():
        print(f"[FAIL] Registry file not found: {REGISTRY_PATH}")
        sys.exit(1)

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    entries = data.get("entries", [])
    if not entries:
        print("[WARN] No entries found in registry.")
        sys.exit(0)

    migrated_count = 0
    not_found_count = 0

    for entry in entries:
        path_str = entry.get("path")
        if not path_str:
            continue
        
        doc_path = REPO_ROOT / path_str
        if not doc_path.exists():
            print(f"[WARN] File not found: {path_str}")
            not_found_count += 1
            continue

        # Extract metadata specifically for frontmatter, omitting "path" itself 
        # and "notes" if they are huge, but generally we can keep all fields.
        frontmatter_data = {k: v for k, v in entry.items() if k != "path" and v is not None}
        
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        match = FRONTMATTER_RE.match(content)
        existing_fm = {}
        body = content

        if match:
            try:
                existing_fm = yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                pass
            body = content[match.end():]

        # Merge frontmatter. Registry takes precedence for governed fields.
        merged_fm = {**existing_fm, **frontmatter_data}

        # Dump to YAML
        new_fm_str = yaml.dump(merged_fm, sort_keys=False, default_flow_style=False)
        new_content = f"---\n{new_fm_str}---\n{body}"

        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"[OK] Migrated {path_str}")
        migrated_count += 1

    print(f"\nMigration complete. Migrated: {migrated_count}, Not Found: {not_found_count}")

if __name__ == "__main__":
    migrate_registry()

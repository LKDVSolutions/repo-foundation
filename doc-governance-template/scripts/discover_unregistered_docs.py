#!/usr/bin/env python3
"""Discover Markdown files in docs/ that are not listed in the generated registry cache."""

import json
import os
from pathlib import Path

def load_registry(registry_path: Path) -> list:
    if not registry_path.exists():
        return []
    with open(registry_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            return data.get('entries', []) if data else []
        except json.JSONDecodeError as e:
            print(f"Error parsing registry cache: {e}")
            return []

def find_all_markdown_files(docs_dir: Path) -> set:
    markdown_files = set()
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                full_path = Path(root) / file
                try:
                    rel_path = full_path.relative_to(docs_dir.parent)
                    markdown_files.add(str(rel_path).replace('\\', '/'))
                except ValueError:
                    pass
    return markdown_files

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / 'docs'
    registry_path = project_root / '.registry_cache.json'

    registry_entries = load_registry(registry_path)
    registered_paths = {entry.get('path') for entry in registry_entries if entry.get('path')}

    all_markdown_files = find_all_markdown_files(docs_dir)

    unregistered_files = all_markdown_files - registered_paths

    if not unregistered_files:
        print("All markdown files in docs/ are currently registered.")
        return

    print(f"Found {len(unregistered_files)} unregistered markdown files:\\n")

    print("Suggested frontmatter registration targets:")
    for file_path in sorted(unregistered_files):
        print(f"- {file_path}")

if __name__ == "__main__":
    main()

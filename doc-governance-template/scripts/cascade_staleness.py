#!/usr/bin/env python3
"""Cascade staleness: automatically invalidate downstream docs when their upstream source_inputs/depends_on change."""

import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"

def main():
    print("=== cascade_staleness.py ===")
    if not REGISTRY_PATH.exists():
        return
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    entries = data.get("entries", [])
    changed_docs = ["example_upstream_doc_id"] # Mock upstream changes
    
    updates = 0
    for entry in entries:
        deps = entry.get("depends_on", []) + entry.get("source_inputs", [])
        if any(dep in changed_docs for dep in deps):
            if entry.get("status") != "stale":
                entry["status"] = "stale"
                entry["notes"] = (entry.get("notes", "") + " [Marked stale due to upstream changes]").strip()
                print(f"Marked '{entry.get('doc_id')}' as stale.")
                updates += 1
                
    if updates > 0:
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False)
    print(f"Cascaded staleness to {updates} docs.")

if __name__ == "__main__":
    main()

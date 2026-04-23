#!/usr/bin/env python3
"""Generate a Governance Health Score."""

import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"

def main():
    print("=== calculate_health_score.py ===")
    if not REGISTRY_PATH.exists():
        print("Score: 0/100 (Missing registry)")
        return
        
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    entries = data.get("entries", [])
    if not entries:
        print("Score: 0/100 (Empty registry)")
        return
        
    total = len(entries)
    active_valid = sum(1 for e in entries if e.get("status") in ("active", "current"))
    stale = sum(1 for e in entries if e.get("status") == "stale")
    
    # Simple score algorithm
    score = max(0, min(100, int((active_valid / total) * 100 - (stale / total) * 50)))
    
    print(f"Governance Health Score: {score}/100")
    print(f"Total Docs: {total}")
    print(f"Active/Valid: {active_valid}")
    print(f"Stale: {stale}")

if __name__ == "__main__":
    main()

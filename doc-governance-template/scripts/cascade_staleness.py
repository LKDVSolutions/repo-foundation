#!/usr/bin/env python3
"""Cascade staleness: mark downstream docs stale when their upstream source_inputs/depends_on change.

Usage:
    python scripts/cascade_staleness.py DOC_REGISTRY_YAML SERVICE_INVENTORY
    python scripts/cascade_staleness.py <doc_id> [<doc_id> ...]
"""

import argparse
import yaml
from filelock import FileLock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"
LOCK_PATH = REGISTRY_PATH.with_suffix(".yaml.lock")


def main() -> None:
    print("=== cascade_staleness.py ===")
    parser = argparse.ArgumentParser(
        description="Mark downstream docs stale when upstream sources change."
    )
    parser.add_argument(
        "changed_doc_ids",
        nargs="+",
        help="doc_id values of changed upstream documents",
    )
    args = parser.parse_args()
    changed_docs = args.changed_doc_ids

    if not REGISTRY_PATH.exists():
        print(f"Registry not found: {REGISTRY_PATH}")
        return

    with FileLock(str(LOCK_PATH), timeout=30):
        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))

        entries = data.get("entries", [])
        updates = 0

        for entry in entries:
            deps = entry.get("depends_on") or []
            source_inputs = entry.get("source_inputs") or []
            all_deps = deps + source_inputs
            if any(dep in changed_docs for dep in all_deps):
                if entry.get("status") != "stale":
                    entry["status"] = "stale"
                    existing_notes = entry.get("notes") or ""
                    entry["notes"] = (existing_notes + " [Marked stale due to upstream changes]").strip()
                    print(f"Marked '{entry.get('doc_id')}' as stale.")
                    updates += 1

        if updates > 0:
            REGISTRY_PATH.write_text(
                yaml.safe_dump(data, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )

    print(f"Cascaded staleness to {updates} docs.")


if __name__ == "__main__":
    main()

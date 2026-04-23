#!/usr/bin/env python3
"""Auto-populate missing schema fields in DOC_REGISTRY.yaml based on inferred metadata."""

import yaml
from filelock import FileLock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"
LOCK_PATH = REGISTRY_PATH.with_suffix(".yaml.lock")


def main() -> None:
    print("=== auto_fix_registry.py ===")
    if not REGISTRY_PATH.exists():
        print("Registry file not found.")
        return

    with FileLock(str(LOCK_PATH), timeout=30):
        try:
            data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Parse error: {e}")
            return

        entries = data.get("entries", [])
        fixed_count = 0

        for entry in entries:
            doc_id = entry.get("doc_id", "<unknown>")

            if "doc_class" not in entry:
                entry["doc_class"] = "active"
                fixed_count += 1

            if "authority_kind" not in entry and entry.get("doc_class") in ("active", "generated"):
                # Do NOT guess authority_kind — it determines which checks apply downstream.
                # Emit a warning so a human assigns the correct value.
                print(f"[WARN] '{doc_id}' missing authority_kind — set to null. Assign manually.")
                entry["authority_kind"] = None
                fixed_count += 1

            if "status" not in entry:
                entry["status"] = "draft"
                fixed_count += 1

            if "depends_on" not in entry or entry.get("depends_on") is None:
                entry["depends_on"] = []
                fixed_count += 1

            if "task_entry_for" not in entry or entry.get("task_entry_for") is None:
                entry["task_entry_for"] = []
                fixed_count += 1

            if "authoritative_for" not in entry or entry.get("authoritative_for") is None:
                entry["authoritative_for"] = []
                fixed_count += 1

            if "system_owner" not in entry:
                entry["system_owner"] = "system-wide"
                fixed_count += 1

            if "doc_owner" not in entry:
                entry["doc_owner"] = "[YOUR-NAME]"
                fixed_count += 1

            if "updated_by" not in entry:
                entry["updated_by"] = "human"
                fixed_count += 1

            if "refresh_policy" not in entry:
                entry["refresh_policy"] = "manual"
                fixed_count += 1

        if fixed_count > 0:
            REGISTRY_PATH.write_text(
                yaml.safe_dump(data, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )
            print(f"Fixed {fixed_count} missing fields in registry.")
        else:
            print("Registry is fully populated.")


if __name__ == "__main__":
    main()

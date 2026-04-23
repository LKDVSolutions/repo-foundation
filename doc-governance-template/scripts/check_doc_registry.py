#!/usr/bin/env python3
"""Check that DOC_REGISTRY.yaml exists, parses, and contains required fields using JSON schema."""

import sys
import yaml
import json
from pathlib import Path
import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"
SCHEMA_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.schema.json"

def check_registry():
    """Run all registry checks. Returns (passed, warnings, failures)."""
    passed = 0
    warnings = 0
    failures = 0

    if not REGISTRY_PATH.exists():
        print(f"[FAIL] Registry file not found: {REGISTRY_PATH.relative_to(REPO_ROOT)}")
        failures += 1
        return passed, warnings, failures
    else:
        print(f"[PASS] Registry file exists: {REGISTRY_PATH.relative_to(REPO_ROOT)}")
        passed += 1

    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        print("[PASS] YAML parses without errors")
        passed += 1
    except yaml.YAMLError as e:
        print(f"[FAIL] YAML parse error: {e}")
        failures += 1
        return passed, warnings, failures

    # Load JSON schema
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception as e:
        print(f"[FAIL] Could not load schema: {e}")
        failures += 1
        return passed, warnings, failures

    # Validate against schema
    try:
        jsonschema.validate(instance=data, schema=schema)
        print("[PASS] JSON Schema validation passed")
        passed += 1
    except jsonschema.exceptions.ValidationError as e:
        print(f"[FAIL] JSON Schema validation failed: {e.message}")
        failures += 1
    
    entries = data.get("entries", [])

    # Check 7: No duplicate doc_ids
    doc_ids = [e.get("doc_id") for e in entries if "doc_id" in e]
    seen_ids: set = set()
    dup_ids: set = set()
    for d in doc_ids:
        if d in seen_ids:
            dup_ids.add(d)
        seen_ids.add(d)
    if dup_ids:
        print(f"[FAIL] Duplicate doc_id values found: {dup_ids}")
        failures += 1
    else:
        print("[PASS] No duplicate doc_id values")
        passed += 1

    # Check 8: No duplicate paths
    paths = [e.get("path") for e in entries if e.get("path")]
    seen_paths: set = set()
    dup_paths: set = set()
    for p in paths:
        if p in seen_paths:
            dup_paths.add(p)
        seen_paths.add(p)
    if dup_paths:
        print(f"[FAIL] Duplicate path values found: {dup_paths}")
        failures += 1
    else:
        print("[PASS] No duplicate path values")
        passed += 1

    # Check: all registered paths exist on disk
    path_missing = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        path_str = entry.get("path")
        if path_str:
            full_path = REPO_ROOT / path_str
            if not full_path.exists():
                path_missing.append(f"'{doc_id}' → {path_str}")
    if path_missing:
        for msg in path_missing:
            print(f"[FAIL] Registered path does not exist on disk: {msg}")
            failures += 1
    else:
        print(f"[PASS] All {len(entries)} registered paths exist on disk")
        passed += 1

    # Check 9: task_entry_for uniqueness (warn only)
    task_class_map: dict[str, list[str]] = {}
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        task_entry_for = entry.get("task_entry_for")
        if task_entry_for and isinstance(task_entry_for, list):
            for tc in task_entry_for:
                task_class_map.setdefault(tc, []).append(doc_id)
    for tc, claiming_docs in task_class_map.items():
        if len(claiming_docs) >= 2:
            print(
                f"[WARN] Task class '{tc}' has {len(claiming_docs)} docs claiming "
                f"task_entry_for: {claiming_docs}"
            )
            warnings += 1
    if all(len(v) == 1 for v in task_class_map.values()):
        print("[PASS] All task classes have exactly one declared entry doc")
        passed += 1
    else:
        print("[PASS] task_entry_for check complete (see warnings above if any)")
        passed += 1

    return passed, warnings, failures

def main():
    print("=== check_doc_registry.py ===")
    passed, warnings, failures = check_registry()
    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)

if __name__ == "__main__":
    main()
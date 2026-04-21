#!/usr/bin/env python3
"""Check that DOC_REGISTRY.yaml exists, parses, and contains required fields."""

import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo_root
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"

VALID_DOC_CLASSES = {"entrypoint", "active", "generated", "historical"}
VALID_AUTHORITY_KINDS = {"plan", "blueprint", "guide", "current_config", "runtime_evidence", None}

REQUIRED_ENTRY_FIELDS = {"doc_id", "path", "doc_class", "authority_kind", "status"}


def check_registry():
    """Run all registry checks. Returns (passed, warnings, failures)."""
    passed = 0
    warnings = 0
    failures = 0

    # Check 1: File exists
    if not REGISTRY_PATH.exists():
        print(f"[FAIL] Registry file not found: {REGISTRY_PATH.relative_to(REPO_ROOT)}")
        failures += 1
        return passed, warnings, failures
    else:
        print(f"[PASS] Registry file exists: {REGISTRY_PATH.relative_to(REPO_ROOT)}")
        passed += 1

    # Check 2: YAML parses without errors
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        print("[PASS] YAML parses without errors")
        passed += 1
    except yaml.YAMLError as e:
        print(f"[FAIL] YAML parse error: {e}")
        failures += 1
        return passed, warnings, failures

    # Check 3: 'entries' key exists and is a non-empty list
    entries = data.get("entries")
    if not isinstance(entries, list) or len(entries) == 0:
        print("[FAIL] 'entries' key missing or empty")
        failures += 1
        return passed, warnings, failures
    else:
        print(f"[PASS] 'entries' key exists with {len(entries)} entries")
        passed += 1

    # Check 4: Each entry has required fields
    missing_fields_found = False
    for i, entry in enumerate(entries):
        doc_id = entry.get("doc_id", f"<entry #{i}>")
        missing = REQUIRED_ENTRY_FIELDS - set(entry.keys())
        if missing:
            print(f"[FAIL] Entry '{doc_id}' missing required fields: {missing}")
            failures += 1
            missing_fields_found = True
    if not missing_fields_found:
        print(
            f"[PASS] All {len(entries)} entries have required fields "
            f"(doc_id, path, doc_class, authority_kind, status)"
        )
        passed += 1

    # Check 5: doc_class values are valid
    invalid_classes = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        dc = entry.get("doc_class")
        if dc not in VALID_DOC_CLASSES:
            invalid_classes.append(f"'{doc_id}' has doc_class='{dc}'")
    if invalid_classes:
        for msg in invalid_classes:
            print(f"[FAIL] Invalid doc_class: {msg} (allowed: {VALID_DOC_CLASSES})")
            failures += 1
    else:
        print(f"[PASS] All doc_class values are valid ({VALID_DOC_CLASSES})")
        passed += 1

    # Check 6: authority_kind values are valid
    invalid_kinds = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        ak = entry.get("authority_kind")
        if ak not in VALID_AUTHORITY_KINDS:
            invalid_kinds.append(f"'{doc_id}' has authority_kind='{ak}'")
    if invalid_kinds:
        for msg in invalid_kinds:
            print(f"[FAIL] Invalid authority_kind: {msg} (allowed: {VALID_AUTHORITY_KINDS})")
            failures += 1
    else:
        print("[PASS] All authority_kind values are valid")
        passed += 1

    # Check 7: No duplicate doc_ids
    doc_ids = [e.get("doc_id") for e in entries]
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

#!/usr/bin/env python3
"""Check that active/generated docs in the registry have required metadata fields."""

import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo_root
REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"


def check_metadata():
    """Run all metadata checks. Returns (passed, warnings, failures)."""
    passed = 0
    warnings = 0
    failures = 0

    if not REGISTRY_PATH.exists():
        print(f"[FAIL] Registry file not found: {REGISTRY_PATH.relative_to(REPO_ROOT)}")
        return passed, warnings, failures + 1

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"[FAIL] YAML parse error: {e}")
            return passed, warnings, failures + 1

    entries = data.get("entries", [])
    if not entries:
        print("[FAIL] No entries found in registry")
        return passed, warnings, failures + 1

    # Check 1: active/generated entries have required metadata fields
    governed_classes = {"active", "generated"}
    required_metadata = [
        "authority_kind",
        "system_owner",
        "doc_owner",
        "updated_by",
        "authoritative_for",
        "refresh_policy",
    ]

    meta_failures = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        doc_class = entry.get("doc_class")
        if doc_class not in governed_classes:
            continue
        for field in required_metadata:
            # authoritative_for can be empty list [] — just must not be absent/None
            if field not in entry or entry[field] is None:
                meta_failures.append(
                    f"'{doc_id}' (doc_class={doc_class}) missing required metadata field: '{field}'"
                )

    if meta_failures:
        for msg in meta_failures:
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        count = sum(1 for e in entries if e.get("doc_class") in governed_classes)
        print(f"[PASS] All {count} active/generated entries have required metadata fields")
        passed += 1

    # Check 2: current_config and runtime_evidence entries have source_inputs and verification_level
    config_kinds = {"current_config", "runtime_evidence"}
    source_failures = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        ak = entry.get("authority_kind")
        if ak not in config_kinds:
            continue
        source_inputs = entry.get("source_inputs")
        if not source_inputs:
            source_failures.append(
                f"'{doc_id}' (authority_kind={ak}) has null/empty source_inputs"
            )
        verification_level = entry.get("verification_level")
        if verification_level is None:
            source_failures.append(
                f"'{doc_id}' (authority_kind={ak}) has null verification_level"
            )

    if source_failures:
        for msg in source_failures:
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        count = sum(1 for e in entries if e.get("authority_kind") in config_kinds)
        print(
            f"[PASS] All {count} current_config/runtime_evidence entries have "
            f"source_inputs and verification_level"
        )
        passed += 1

    # Check 3: runtime_evidence entries have last_verified (warn if null)
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        ak = entry.get("authority_kind")
        if ak != "runtime_evidence":
            continue
        last_verified = entry.get("last_verified")
        if last_verified is None:
            print(
                f"[WARN] '{doc_id}' (authority_kind=runtime_evidence) has null last_verified "
                f"— no verification date on record"
            )
            warnings += 1
        else:
            print(f"[PASS] '{doc_id}' (runtime_evidence) has last_verified: {last_verified}")
            passed += 1

    # Check 4: superseded_by references exist in registry and no cycles
    all_doc_ids = {e.get("doc_id") for e in entries if e.get("doc_id")}
    entry_dict = {e.get("doc_id"): e for e in entries if e.get("doc_id")}
    supersession_failures = []
    for entry in entries:
        doc_id = entry.get("doc_id", "<unknown>")
        superseded_by = entry.get("superseded_by")
        if superseded_by:
            if superseded_by not in all_doc_ids:
                supersession_failures.append(
                    f"'{doc_id}' superseded_by='{superseded_by}' but that doc_id does not exist in registry"
                )
            else:
                # Cycle detection
                visited = {doc_id}
                current = superseded_by
                while current:
                    if current in visited:
                        supersession_failures.append(f"Cycle detected in superseded_by starting at '{doc_id}'")
                        break
                    visited.add(current)
                    curr_entry = entry_dict.get(current)
                    current = curr_entry.get("superseded_by") if curr_entry else None

    if supersession_failures:
        for msg in supersession_failures:
            print(f"[FAIL] {msg}")
            failures += 1
    else:
        count = sum(1 for e in entries if e.get("superseded_by"))
        if count == 0:
            print("[PASS] No superseded_by references to check")
        else:
            print(f"[PASS] All {count} superseded_by references resolve to existing doc_ids")
        passed += 1

    return passed, warnings, failures


def main():
    print("=== check_doc_metadata.py ===")
    passed, warnings, failures = check_metadata()
    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()

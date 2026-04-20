#!/usr/bin/env python3
"""Check that DOC_REGISTRY.md matches the current rendered output from DOC_REGISTRY.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure scripts directory is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_doc_registry_md import REGISTRY_MD, REGISTRY_YAML, load_registry_entries, render_registry_md

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo_root


def check_registry_sync():
    """Return (passed, warnings, failures) for DOC_REGISTRY markdown sync."""
    passed = 0
    warnings = 0
    failures = 0

    if not REGISTRY_YAML.exists():
        print(f"[FAIL] Registry YAML not found: {REGISTRY_YAML.relative_to(REPO_ROOT)}")
        return passed, warnings, failures + 1

    if not REGISTRY_MD.exists():
        print(f"[FAIL] Generated registry Markdown not found: {REGISTRY_MD.relative_to(REPO_ROOT)}")
        return passed, warnings, failures + 1

    entries = load_registry_entries()
    expected = render_registry_md(entries)
    actual = REGISTRY_MD.read_text(encoding="utf-8")

    if actual != expected:
        print(
            "[FAIL] DOC_REGISTRY.md is out of sync with DOC_REGISTRY.yaml "
            "— run `python scripts/build_doc_registry_md.py`"
        )
        failures += 1
    else:
        print("[PASS] DOC_REGISTRY.md is in sync with DOC_REGISTRY.yaml")
        passed += 1

    return passed, warnings, failures


def main():
    print("=== check_doc_registry_sync.py ===")
    passed, warnings, failures = check_registry_sync()
    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()

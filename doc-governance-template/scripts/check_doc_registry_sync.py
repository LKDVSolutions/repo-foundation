#!/usr/bin/env python3
"""Check that DOC_REGISTRY.md matches the current rendered output from frontmatter."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure scripts directory is importable regardless of working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aggregate_registry import REGISTRY_MD, extract_governed_entries, render_registry_md

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo_root


def load_registry_entries():
    """Return registry entries via aggregate_registry for compatibility."""
    return extract_governed_entries()


def check_registry_sync():
    """Return (passed, warnings, failures) for DOC_REGISTRY markdown sync."""
    passed = 0
    warnings = 0
    failures = 0

    if not REGISTRY_MD.exists():
        print(f"[FAIL] Generated registry Markdown not found: {REGISTRY_MD.relative_to(REPO_ROOT)}")
        return passed, warnings, failures + 1

    entries = load_registry_entries()
    expected = render_registry_md(entries)
    actual = REGISTRY_MD.read_text(encoding="utf-8")

    if actual != expected:
        print(
            "[FAIL] DOC_REGISTRY.md is out of sync with frontmatter "
            "— run `python scripts/aggregate_registry.py`"
        )
        failures += 1
    else:
        print("[PASS] DOC_REGISTRY.md is in sync with frontmatter")
        passed += 1

    return passed, warnings, failures


def main():
    print("=== check_doc_registry_sync.py ===")
    passed, warnings, failures = check_registry_sync()
    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Documentation quality gate. Run with --fast for core checks, --full for all checks.

Usage:
    python scripts/docs_gate.py --fast    # registry + metadata + sync (default)
    python scripts/docs_gate.py --full    # adds broken link validation
"""

import sys
import argparse
from pathlib import Path

# Ensure the scripts directory is importable from any working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_doc_registry import check_registry
from check_doc_registry_sync import check_registry_sync
from check_doc_metadata import check_metadata
from validate_doc_links import check_links
from detect_drift import check_evidence_freshness


def run_gate(fast: bool = True) -> int:
    """Run the docs gate. Returns exit code (0 = pass, 1 = failures present)."""
    total_passed = 0
    total_warnings = 0
    total_failures = 0

    # --- Fast checks (always run) ---
    print()
    p, w, f = check_registry()
    total_passed += p
    total_warnings += w
    total_failures += f

    print()
    p, w, f = check_metadata()
    total_passed += p
    total_warnings += w
    total_failures += f

    print()
    p, w, f = check_registry_sync()
    total_passed += p
    total_warnings += w
    total_failures += f

    print()
    p, w, f = check_evidence_freshness()
    total_passed += p
    total_warnings += w
    total_failures += f

    # --- Full checks (adds link validation) ---
    if not fast:
        print()
        p, w, f = check_links()
        total_passed += p
        total_warnings += w
        total_failures += f

    # --- Summary ---
    print()
    print("=" * 50)
    mode = "fast" if fast else "full"
    print(
        f"docs_gate [{mode}] summary: "
        f"{total_passed} passed, {total_warnings} warnings, {total_failures} failures"
    )
    if total_failures == 0:
        print("Gate: PASS")
    else:
        print("Gate: FAIL")
    print("=" * 50)

    return 0 if total_failures == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="Documentation quality gate.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--fast",
        action="store_true",
        default=False,
        help="Run fast checks only: registry + metadata + sync (default if no flag given)",
    )
    mode_group.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Run all checks including validate_doc_links",
    )
    args = parser.parse_args()

    # Default to --fast if neither flag is given
    fast = not args.full

    sys.exit(run_gate(fast=fast))


if __name__ == "__main__":
    main()

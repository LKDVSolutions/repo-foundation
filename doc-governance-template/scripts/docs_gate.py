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
from check_shell_scripts import check_shell_scripts
from validate_doc_links import check_links
from detect_drift import check_evidence_freshness
try:
    from governance_logger import get_governance_logger
except ImportError:  # pragma: no cover - used when imported as scripts.docs_gate
    from scripts.governance_logger import get_governance_logger


LOGGER = get_governance_logger("docs_gate.py")


def run_gate(fast: bool = True) -> int:
    """Run the docs gate. Returns exit code (0 = pass, 1 = failures present)."""
    total_passed = 0
    total_warnings = 0
    total_failures = 0
    mode = "fast" if fast else "full"

    LOGGER.log("INFO", "gate_start", f"Starting docs gate in {mode} mode", doc_id="DOCS_GATE")

    # --- Fast checks (always run) ---
    LOGGER.log("INFO", "check_start", "Running check_doc_registry", doc_id="DOC_REGISTRY")
    p, w, f = check_registry()
    total_passed += p
    total_warnings += w
    total_failures += f
    LOGGER.log("INFO", "check_complete", f"check_doc_registry results: pass={p}, warn={w}, fail={f}", doc_id="DOC_REGISTRY")

    LOGGER.log("INFO", "check_start", "Running check_doc_metadata", doc_id="DOC_METADATA")
    p, w, f = check_metadata()
    total_passed += p
    total_warnings += w
    total_failures += f
    LOGGER.log("INFO", "check_complete", f"check_doc_metadata results: pass={p}, warn={w}, fail={f}", doc_id="DOC_METADATA")

    LOGGER.log("INFO", "check_start", "Running check_doc_registry_sync", doc_id="DOC_REGISTRY")
    p, w, f = check_registry_sync()
    total_passed += p
    total_warnings += w
    total_failures += f
    LOGGER.log("INFO", "check_complete", f"check_doc_registry_sync results: pass={p}, warn={w}, fail={f}", doc_id="DOC_REGISTRY")

    LOGGER.log("INFO", "check_start", "Running check_evidence_freshness", doc_id="RUNTIME_EVIDENCE")
    p, w, f = check_evidence_freshness()
    total_passed += p
    total_warnings += w
    total_failures += f
    LOGGER.log("INFO", "check_complete", f"check_evidence_freshness results: pass={p}, warn={w}, fail={f}", doc_id="RUNTIME_EVIDENCE")

    LOGGER.log("INFO", "check_start", "Running check_shell_scripts", doc_id="ENGINEERING_STANDARDS")
    p, w, f = check_shell_scripts()
    total_passed += p
    total_warnings += w
    total_failures += f
    LOGGER.log("INFO", "check_complete", f"check_shell_scripts results: pass={p}, warn={w}, fail={f}", doc_id="ENGINEERING_STANDARDS")

    # --- Full checks (adds link validation) ---
    if not fast:
        LOGGER.log("INFO", "check_start", "Running validate_doc_links", doc_id="DOC_LINKS")
        p, w, f = check_links()
        total_passed += p
        total_warnings += w
        total_failures += f
        LOGGER.log("INFO", "check_complete", f"validate_doc_links results: pass={p}, warn={w}, fail={f}", doc_id="DOC_LINKS")

    # --- Summary ---
    summary = (
        f"docs_gate [{mode}] summary: "
        f"{total_passed} passed, {total_warnings} warnings, {total_failures} failures"
    )
    if total_failures == 0:
        LOGGER.log("INFO", "gate_summary", summary, doc_id="DOCS_GATE")
        LOGGER.log("INFO", "gate_result", "Gate: PASS", doc_id="DOCS_GATE")
    else:
        LOGGER.log("ERROR", "gate_summary", summary, doc_id="DOCS_GATE")
        LOGGER.log("ERROR", "gate_result", "Gate: FAIL", doc_id="DOCS_GATE")

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

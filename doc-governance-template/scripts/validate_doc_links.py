#!/usr/bin/env python3
"""Validate that internal markdown links in key docs resolve to real files."""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # scripts/ -> repo_root

# Core governance docs to check for broken links.
# Extend this list to include your project's key blueprint or index docs.
DOCS_TO_CHECK = [
    REPO_ROOT / "docs/INDEX.md",
    REPO_ROOT / "docs/REFERENCE.md",
    REPO_ROOT / "docs/development/AGENT_WORKFLOW.md",
    REPO_ROOT / "docs/reference/registry/DOC_REGISTRY.md",
]

# Regex to find markdown links: [text](path)
LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')


def extract_links(content: str) -> list[str]:
    return [m.group(2) for m in LINK_RE.finditer(content)]


def is_external(link: str) -> bool:
    return link.startswith("http://") or link.startswith("https://")


def is_anchor_only(link: str) -> bool:
    return link.startswith("#")


def resolve_link(link: str, doc_path: Path) -> Path | None:
    if "#" in link:
        link = link[: link.index("#")]
    if not link:
        return None
    return (doc_path.parent / link).resolve()


def check_links():
    """Run link checks for all scoped docs. Returns (passed, warnings, failures)."""
    passed = 0
    warnings = 0
    failures = 0

    for doc_path in DOCS_TO_CHECK:
        if not doc_path.exists():
            print(f"[WARN] Scoped doc not found (skipping): {doc_path.relative_to(REPO_ROOT)}")
            warnings += 1
            continue

        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        links = extract_links(content)
        rel_doc = doc_path.relative_to(REPO_ROOT)

        doc_failures = 0
        doc_skipped = 0
        doc_passed = 0

        for link in links:
            if is_external(link):
                doc_skipped += 1
                continue
            if is_anchor_only(link):
                doc_skipped += 1
                continue

            resolved = resolve_link(link, doc_path)
            if resolved is None:
                doc_skipped += 1
                continue

            if not resolved.exists():
                try:
                    resolved_rel = resolved.relative_to(REPO_ROOT)
                except ValueError:
                    resolved_rel = resolved
                print(f"[FAIL] Broken link in {rel_doc}: '{link}' -> {resolved_rel}")
                failures += 1
                doc_failures += 1
            else:
                doc_passed += 1

        if doc_failures == 0:
            print(
                f"[PASS] {rel_doc} — {doc_passed} internal links valid, "
                f"{doc_skipped} external/anchor links skipped"
            )
            passed += 1

    return passed, warnings, failures


def main():
    print("=== validate_doc_links.py ===")
    passed, warnings, failures = check_links()
    print(f"\nResult: {passed} docs fully valid, {warnings} warnings, {failures} broken links")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()

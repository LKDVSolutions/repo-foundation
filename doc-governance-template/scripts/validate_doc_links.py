#!/usr/bin/env python3
"""Validate that internal markdown links in governed docs resolve to real files.

Scope: all active and generated docs registered in DOC_REGISTRY.yaml.
Falls back to a hardcoded list of core docs if the registry is unavailable.
"""

import re
import sys
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REGISTRY_PATH = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"

# Fallback list used only when the registry cannot be loaded
FALLBACK_DOCS = [
    REPO_ROOT / "docs/INDEX.md",
    REPO_ROOT / "docs/REFERENCE.md",
    REPO_ROOT / "docs/development/AGENT_WORKFLOW.md",
    REPO_ROOT / "docs/reference/registry/DOC_REGISTRY.md",
]

LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')


def get_docs_to_check() -> list[Path]:
    """Return all active/generated docs from the registry."""
    if not REGISTRY_PATH.exists():
        print(f"[WARN] Registry not found — falling back to hardcoded doc list")
        return [p for p in FALLBACK_DOCS if p.exists()]

    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"[WARN] Could not load registry ({e}) — falling back to hardcoded doc list")
        return [p for p in FALLBACK_DOCS if p.exists()]

    entries = data.get("entries", [])
    governed = {"active", "generated"}
    paths = []
    for entry in entries:
        if entry.get("doc_class") in governed and entry.get("path"):
            p = REPO_ROOT / entry["path"]
            if p.exists() and p.suffix == ".md":
                paths.append(p)
    return paths


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
    try:
        return (doc_path.parent / link).resolve(strict=False)
    except RuntimeError:
        return None


def check_links():
    """Run link checks for all scoped docs. Returns (passed, warnings, failures)."""
    passed = 0
    warnings = 0
    failures = 0

    docs_to_check = get_docs_to_check()

    if not docs_to_check:
        print("[WARN] No docs found to check")
        warnings += 1
        return passed, warnings, failures

    for doc_path in docs_to_check:
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

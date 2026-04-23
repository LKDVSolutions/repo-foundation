#!/usr/bin/env python3
"""CLI to automatically repair missing frontmatter and append missing standard headings.

Usage:
    python scripts/auto_fix.py             # dry-run (safe, no changes made)
    python scripts/auto_fix.py --apply     # apply fixes
"""

import os
import argparse
from pathlib import Path

# Directories skipped entirely — intentional non-standard markdown (prompts, templates)
EXCLUDE_DIRS = {
    "docs/plans/prompts",
    "docs/plans/templates",
}

# Sentinel title injected when frontmatter is auto-generated.
# The docs gate rejects this value — a human must replace it before the gate passes.
_SENTINEL_TITLE = "FIXME-NEEDS-TITLE"


def fix_markdown_file(path: Path, repo_root: Path, apply: bool) -> bool:
    rel = path.relative_to(repo_root)

    for excl in EXCLUDE_DIRS:
        try:
            rel.relative_to(excl)
            return False
        except ValueError:
            pass

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    if not content.startswith("---\n"):
        # Inject sentinel values so the gate fails until a human corrects them.
        frontmatter = f"---\ntitle: {_SENTINEL_TITLE}\nstatus: draft\n---\n"
        content = frontmatter + content

    if "## Governance" not in content and "## Introduction" not in content:
        content = content.rstrip() + "\n\n## Governance\n\nThis section was auto-added by auto_fix.py.\n"

    if content != original:
        if apply:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[FIXED] {rel}")
        else:
            print(f"[DRY-RUN] Would fix: {rel}")
        return True

    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-repair markdown files.")
    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
        help="Apply fixes. Without this flag, runs in dry-run mode (no files changed).",
    )
    args = parser.parse_args()

    if not args.apply:
        print("=== auto_fix.py [DRY-RUN — pass --apply to make changes] ===")
    else:
        print("=== auto_fix.py [APPLY] ===")

    repo_root = Path(__file__).resolve().parent.parent
    docs_dir = repo_root / "docs"

    fixes = 0
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md"):
                if fix_markdown_file(Path(root) / file, repo_root, apply=args.apply):
                    fixes += 1

    label = "fixed" if args.apply else "would fix"
    print(f"Total files {label}: {fixes}")


if __name__ == "__main__":
    main()

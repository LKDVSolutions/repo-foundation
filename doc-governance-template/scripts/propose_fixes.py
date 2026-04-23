#!/usr/bin/env python3
"""Shadow-mode documentation fix proposal engine.

This script REPLACES auto_fix.py. It never mutates source files directly.
Instead, it identifies violations, generates unified diffs (patches), and writes
them to .shadow/. A human or a CI-controlled privileged step must review and
apply them with: patch -p1 < .shadow/<filename>.patch

This enforces the "System proposes; human disposes" governance principle and
eliminates the risk of an agent entering a self-healing corruption loop.

Usage:
    python scripts/propose_fixes.py           # scan and write patches to .shadow/
    python scripts/propose_fixes.py --report  # print a summary only, no patch files written
    python scripts/propose_fixes.py --apply   # DANGER: apply all pending patches in .shadow/

Idempotency guarantee: re-running the script will not overwrite an existing
patch for the same file unless the expected fix has changed.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SHADOW_DIR = REPO_ROOT / ".shadow"

# Directories whose Markdown is intentionally non-standard and must be excluded
EXCLUDE_DIRS = {
    "docs/plans/prompts",
    "docs/plans/templates",
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

# Required frontmatter fields for any governed doc. The gate enforces these.
REQUIRED_FIELDS = ["doc_id", "doc_class", "title", "status", "system_owner", "doc_owner"]


# ---------------------------------------------------------------------------
# Patch generation helpers
# ---------------------------------------------------------------------------

def _unified_diff(original: str, proposed: str, rel_path: str) -> str:
    """Generate a unified diff string between original and proposed content."""
    original_lines = original.splitlines(keepends=True)
    proposed_lines = proposed.splitlines(keepends=True)
    diff = difflib.unified_diff(
        original_lines,
        proposed_lines,
        fromfile=f"a/{rel_path}",
        tofile=f"b/{rel_path}",
    )
    return "".join(diff)


def _patch_filename(rel_path: str, fix_kind: str) -> str:
    """Generate a deterministic, collision-safe patch filename."""
    safe_path = rel_path.replace("/", "__").replace(".", "_")
    return f"{fix_kind}__{safe_path}.patch"


def _write_patch(shadow_dir: Path, patch_name: str, diff_content: str, dry_run: bool) -> bool:
    """Write a patch file to .shadow/ — idempotent: skips if identical patch exists.
    
    Returns True if a new/changed patch was written.
    """
    patch_path = shadow_dir / patch_name
    content_hash = hashlib.sha256(diff_content.encode()).hexdigest()[:12]
    
    # Idempotency: if identical patch already exists, skip
    if patch_path.exists():
        existing = patch_path.read_text(encoding="utf-8")
        if existing == diff_content:
            return False  # already proposed, nothing to do

    if not dry_run:
        shadow_dir.mkdir(parents=True, exist_ok=True)
        patch_path.write_text(diff_content, encoding="utf-8")

    return True


# ---------------------------------------------------------------------------
# Violation detectors — each returns (proposed_content, fix_kind) or None
# ---------------------------------------------------------------------------

def _propose_frontmatter(content: str, rel_path: str) -> str | None:
    """Propose minimal frontmatter if the file has none."""
    if content.startswith("---\n"):
        return None  # already has frontmatter

    stem = Path(rel_path).stem.upper().replace("-", "_").replace(" ", "_")
    proposed_fm = {
        "doc_id": stem,
        "doc_class": "active",
        "title": f"NEEDS-TITLE — {stem}",
        "status": "draft",
        "system_owner": "NEEDS-OWNER",
        "doc_owner": "NEEDS-OWNER",
        "updated_by": "agent",
        "refresh_policy": "manual",
    }
    fm_str = yaml.dump(proposed_fm, sort_keys=False, default_flow_style=False)
    return f"---\n{fm_str}---\n{content}"


def _propose_missing_fields(content: str, rel_path: str) -> str | None:
    """Propose additions to frontmatter when required fields are absent."""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None  # no frontmatter — handled by _propose_frontmatter
    
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return None  # malformed YAML — not safe to auto-propose
    
    missing = [f for f in REQUIRED_FIELDS if f not in fm or fm[f] is None]
    if not missing:
        return None

    for field in missing:
        fm[field] = f"NEEDS-{field.upper().replace('_', '-')}"

    fm_str = yaml.dump(fm, sort_keys=False, default_flow_style=False)
    body = content[match.end():]
    return f"---\n{fm_str}---\n{body}"


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------

def scan_and_propose(
    docs_dir: Path,
    shadow_dir: Path,
    dry_run: bool,
) -> list[dict]:
    """Scan all Markdown files, identify violations, generate patches.
    
    Returns a list of proposal dicts for reporting.
    """
    proposals = []

    for root, _dirs, files in os.walk(docs_dir):
        for filename in sorted(files):
            if not filename.endswith(".md"):
                continue

            file_path = Path(root) / filename
            rel = str(file_path.relative_to(REPO_ROOT))

            # Respect exclusion list
            excluded = False
            for excl in EXCLUDE_DIRS:
                try:
                    Path(rel).relative_to(excl)
                    excluded = True
                    break
                except ValueError:
                    pass
            if excluded:
                continue

            try:
                original = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            # Run each violation detector in priority order
            detectors = [
                ("missing-frontmatter", _propose_frontmatter),
                ("missing-required-fields", _propose_missing_fields),
            ]

            for fix_kind, detector in detectors:
                proposed = detector(original, rel)
                if proposed is None:
                    continue

                diff = _unified_diff(original, proposed, rel)
                if not diff:
                    continue

                patch_name = _patch_filename(rel, fix_kind)
                was_written = _write_patch(shadow_dir, patch_name, diff, dry_run=dry_run)

                proposals.append({
                    "file": rel,
                    "fix_kind": fix_kind,
                    "patch": patch_name,
                    "new": was_written,
                })
                # Only propose the first violation per file: frontmatter
                # must be fixed before we can reason about field completeness
                break

    return proposals


# ---------------------------------------------------------------------------
# Apply mode — privileged action
# ---------------------------------------------------------------------------

def apply_patches(shadow_dir: Path) -> int:
    """Apply all .patch files in .shadow/ using the `patch` CLI.
    
    This is the ONLY path that modifies source files. Requires explicit --apply flag.
    Returns count of patches applied.
    """
    patch_files = sorted(shadow_dir.glob("*.patch"))
    if not patch_files:
        print("[INFO] No pending patches in .shadow/")
        return 0

    applied = 0
    for patch_file in patch_files:
        print(f"  [APPLY] {patch_file.name}")
        result = subprocess.run(
            ["patch", "-p1", "--input", str(patch_file)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            patch_file.unlink()  # Remove applied patch — idempotent cleanup
            print(f"    ✓ Applied and removed: {patch_file.name}")
            applied += 1
        else:
            print(f"    ✗ FAILED to apply {patch_file.name}:")
            print(f"      {result.stderr.strip()}")

    return applied


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Propose documentation fixes as patch files in .shadow/.",
        epilog=(
            "By default, patches are written to .shadow/. "
            "Use --report to preview without writing. "
            "Use --apply to apply pending patches in .shadow/ to source files."
        ),
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print a summary of violations without writing any patch files.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply all pending patches in .shadow/ to source files. Requires review.",
    )
    args = parser.parse_args()

    if args.apply and args.report:
        print("[ERROR] --apply and --report are mutually exclusive.")
        sys.exit(1)

    if args.apply:
        print("=== propose_fixes.py [APPLY MODE] ===")
        applied = apply_patches(SHADOW_DIR)
        print(f"\nPatches applied: {applied}")
        sys.exit(0)

    dry_run = args.report
    mode_label = "REPORT (dry-run)" if dry_run else "PROPOSE"
    print(f"=== propose_fixes.py [{mode_label}] ===")

    proposals = scan_and_propose(
        docs_dir=REPO_ROOT / "docs",
        shadow_dir=SHADOW_DIR,
        dry_run=dry_run,
    )

    if not proposals:
        print("\n[PASS] No violations found. No patches proposed.")
        sys.exit(0)

    print(f"\n{'Violations found' if dry_run else 'Patches written'}: {len(proposals)}")
    for p in proposals:
        status = "(new)" if p["new"] else "(unchanged)"
        if dry_run:
            print(f"  [{p['fix_kind']}] {p['file']}")
        else:
            print(f"  [{p['fix_kind']}] {p['file']} → .shadow/{p['patch']} {status}")

    if not dry_run:
        print(
            f"\nReview patches in .shadow/ then run: "
            f"python scripts/propose_fixes.py --apply"
        )

    sys.exit(1 if proposals else 0)


if __name__ == "__main__":
    main()

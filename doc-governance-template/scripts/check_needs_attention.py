---
doc_id: CHECK_NEEDS_ATTENTION
doc_class: active
authority_kind: current_config
title: "check_needs_attention.py \u2014 CI Escalation Gate"
primary_audience: agents
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: agent
authoritative_for:
- CI enforcement of NEEDS_ATTENTION.md open blocker detection
source_inputs:
- docs/plans/NEEDS_ATTENTION.md
verification_level: repo_derived
refresh_policy: on_source_change
status: active
depends_on: []
---
#!/usr/bin/env python3
"""Check that docs/plans/NEEDS_ATTENTION.md has no open (unresolved) agent blockers.

A blocker is considered open if it contains a markdown unchecked item: `- [ ]`
It is resolved when replaced with: `- [x]`

Usage:
    python scripts/check_needs_attention.py
"""

import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NEEDS_ATTENTION_PATH = REPO_ROOT / "docs" / "plans" / "NEEDS_ATTENTION.md"

_OPEN_ITEM_RE = re.compile(r"^\s*-\s+\[ \]", re.MULTILINE)


def check_needs_attention() -> tuple[int, int, int]:
    """Return (passed, warnings, failures)."""
    passed = 0
    warnings = 0
    failures = 0

    if not NEEDS_ATTENTION_PATH.exists():
        print(f"[PASS] {NEEDS_ATTENTION_PATH.name} not found — no open blockers")
        return passed + 1, warnings, failures

    content = NEEDS_ATTENTION_PATH.read_text(encoding="utf-8")
    open_items = _OPEN_ITEM_RE.findall(content)

    if open_items:
        print(
            f"[FAIL] NEEDS_ATTENTION.md has {len(open_items)} open blocker(s) — "
            f"resolve or mark as [x] before merging"
        )
        for line in content.splitlines():
            if re.match(r"^\s*-\s+\[ \]", line):
                print(f"  {line.strip()}")
        failures += 1
    else:
        print("[PASS] NEEDS_ATTENTION.md has no open blockers")
        passed += 1

    return passed, warnings, failures


def main() -> None:
    print("=== check_needs_attention.py ===")
    passed, warnings, failures = check_needs_attention()
    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()

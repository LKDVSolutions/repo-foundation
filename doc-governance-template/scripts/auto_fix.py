#!/usr/bin/env python3
"""DEPRECATED: auto_fix.py has been superseded by propose_fixes.py.

Use instead:
    python scripts/propose_fixes.py           # propose patches to .shadow/
    python scripts/propose_fixes.py --report  # dry-run report
    python scripts/propose_fixes.py --apply   # apply reviewed patches
"""

import sys


def main() -> int:
    print(
        "[DEPRECATED] auto_fix.py is retired. "
        "Use scripts/propose_fixes.py instead.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())

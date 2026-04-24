"""Retired tests for deprecated auto_fix.py.

The legacy script intentionally exits at import/entry time and has been replaced by
scripts/propose_fixes.py. Keeping these tests active causes pytest collection
failures, so this module is intentionally skipped.
"""

import pytest


pytestmark = pytest.mark.skip(reason="Legacy auto_fix.py retired; use propose_fixes.py tests")

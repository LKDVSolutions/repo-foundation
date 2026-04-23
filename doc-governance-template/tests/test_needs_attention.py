import pytest
from pathlib import Path
from unittest.mock import patch

from scripts.check_needs_attention import check_needs_attention


def _run(tmp_path, content):
    na = tmp_path / "NEEDS_ATTENTION.md"
    na.write_text(content)
    with patch("scripts.check_needs_attention.NEEDS_ATTENTION_PATH", na):
        return check_needs_attention()


def test_no_open_items_passes(tmp_path):
    passed, warnings, failures = _run(tmp_path, "# NEEDS_ATTENTION\n\n- [x] Resolved: fixed the thing\n")
    assert failures == 0
    assert passed == 1


def test_open_item_fails(tmp_path):
    passed, warnings, failures = _run(tmp_path, "# NEEDS_ATTENTION\n\n- [ ] Agent blocked: missing dep\n")
    assert failures == 1


def test_multiple_open_items_fails(tmp_path):
    content = "# NEEDS_ATTENTION\n\n- [ ] First blocker\n- [ ] Second blocker\n"
    passed, warnings, failures = _run(tmp_path, content)
    assert failures == 1


def test_mixed_open_and_resolved_fails(tmp_path):
    content = "# NEEDS_ATTENTION\n\n- [x] Done\n- [ ] Still open\n"
    passed, warnings, failures = _run(tmp_path, content)
    assert failures == 1


def test_empty_file_passes(tmp_path):
    passed, warnings, failures = _run(tmp_path, "")
    assert failures == 0


def test_missing_file_passes(tmp_path):
    missing = tmp_path / "NEEDS_ATTENTION.md"
    with patch("scripts.check_needs_attention.NEEDS_ATTENTION_PATH", missing):
        passed, warnings, failures = check_needs_attention()
    assert failures == 0
    assert passed == 1

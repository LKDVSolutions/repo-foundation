import pytest
from pathlib import Path

from scripts.auto_fix import fix_markdown_file, _SENTINEL_TITLE


def test_injects_sentinel_frontmatter_when_missing(tmp_path):
    doc = tmp_path / "docs" / "test.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# My Doc\n\nSome content.\n\n## Governance\n")

    changed = fix_markdown_file(doc, tmp_path, apply=True)

    assert changed
    content = doc.read_text()
    assert content.startswith("---\n")
    assert f"title: {_SENTINEL_TITLE}" in content
    assert "status: draft" in content


def test_sentinel_title_is_not_active(tmp_path):
    """Injected frontmatter must use draft status so the gate flags it."""
    doc = tmp_path / "docs" / "test.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("# My Doc\n\n## Governance\n")

    fix_markdown_file(doc, tmp_path, apply=True)
    content = doc.read_text()

    assert "status: active" not in content
    assert "status: draft" in content


def test_does_not_modify_file_with_frontmatter_and_governance(tmp_path):
    original = "---\ntitle: Real Title\nstatus: active\n---\n\n# Doc\n\n## Governance\n\nContent.\n"
    doc = tmp_path / "docs" / "test.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(original)

    changed = fix_markdown_file(doc, tmp_path, apply=True)

    assert not changed
    assert doc.read_text() == original


def test_excludes_prompts_directory(tmp_path):
    doc = tmp_path / "docs" / "plans" / "prompts" / "PROMPT.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("No frontmatter here.\n")

    changed = fix_markdown_file(doc, tmp_path, apply=True)

    assert not changed
    assert doc.read_text() == "No frontmatter here.\n"


def test_dry_run_does_not_write(tmp_path):
    original = "# No frontmatter\n\n## Governance\n"
    doc = tmp_path / "docs" / "test.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(original)

    changed = fix_markdown_file(doc, tmp_path, apply=False)

    assert changed
    assert doc.read_text() == original  # no change applied

from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts import propose_fixes


def test_scan_and_propose_generates_frontmatter_patch(tmp_path):
    docs_dir = tmp_path / "docs"
    shadow_dir = tmp_path / ".shadow"
    docs_dir.mkdir(parents=True)
    doc = docs_dir / "sample.md"
    doc.write_text("# Hello\n", encoding="utf-8")

    with patch("scripts.propose_fixes.REPO_ROOT", tmp_path):
        proposals = propose_fixes.scan_and_propose(docs_dir=docs_dir, shadow_dir=shadow_dir, dry_run=False)

    assert len(proposals) == 1
    patch_file = shadow_dir / proposals[0]["patch"]
    assert patch_file.exists()
    patch_text = patch_file.read_text(encoding="utf-8")
    assert "a/docs/sample.md" in patch_text
    assert "b/docs/sample.md" in patch_text


def test_scan_and_propose_is_idempotent(tmp_path):
    docs_dir = tmp_path / "docs"
    shadow_dir = tmp_path / ".shadow"
    docs_dir.mkdir(parents=True)
    doc = docs_dir / "sample.md"
    doc.write_text("# Hello\n", encoding="utf-8")

    with patch("scripts.propose_fixes.REPO_ROOT", tmp_path):
        first = propose_fixes.scan_and_propose(docs_dir=docs_dir, shadow_dir=shadow_dir, dry_run=False)
        second = propose_fixes.scan_and_propose(docs_dir=docs_dir, shadow_dir=shadow_dir, dry_run=False)

    assert first[0]["new"] is True
    assert second[0]["new"] is False


def test_scan_and_propose_report_mode_does_not_write_patches(tmp_path):
    docs_dir = tmp_path / "docs"
    shadow_dir = tmp_path / ".shadow"
    docs_dir.mkdir(parents=True)
    doc = docs_dir / "sample.md"
    doc.write_text("# Hello\n", encoding="utf-8")

    with patch("scripts.propose_fixes.REPO_ROOT", tmp_path):
        proposals = propose_fixes.scan_and_propose(docs_dir=docs_dir, shadow_dir=shadow_dir, dry_run=True)

    assert len(proposals) == 1
    assert not shadow_dir.exists()


def test_apply_patches_applies_success_and_removes_patch(tmp_path):
    shadow_dir = tmp_path / ".shadow"
    shadow_dir.mkdir(parents=True)
    patch_file = shadow_dir / "change.patch"
    patch_file.write_text("dummy patch", encoding="utf-8")

    with patch("scripts.propose_fixes.REPO_ROOT", tmp_path), \
         patch("scripts.propose_fixes.subprocess.run") as run_mock:
        run_mock.return_value = MagicMock(returncode=0, stderr="")
        applied = propose_fixes.apply_patches(shadow_dir)

    assert applied == 1
    assert not patch_file.exists()


def test_apply_patches_keeps_failed_patch(tmp_path):
    shadow_dir = tmp_path / ".shadow"
    shadow_dir.mkdir(parents=True)
    patch_file = shadow_dir / "change.patch"
    patch_file.write_text("dummy patch", encoding="utf-8")

    with patch("scripts.propose_fixes.REPO_ROOT", tmp_path), \
         patch("scripts.propose_fixes.subprocess.run") as run_mock:
        run_mock.return_value = MagicMock(returncode=1, stderr="reject")
        applied = propose_fixes.apply_patches(shadow_dir)

    assert applied == 0
    assert patch_file.exists()

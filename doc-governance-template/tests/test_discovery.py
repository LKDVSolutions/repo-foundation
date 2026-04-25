import os
import sys
import json
import pytest
from pathlib import Path

# Add project root to python path so 'scripts' can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.discover_unregistered_docs import load_registry, find_all_markdown_files

def test_load_registry_empty(tmp_path):
    registry_file = tmp_path / ".registry_cache.json"
    # File doesn't exist
    assert load_registry(registry_file) == []
    
    # Empty file
    registry_file.write_text("")
    assert load_registry(registry_file) == []

def test_load_registry_valid(tmp_path):
    registry_file = tmp_path / ".registry_cache.json"
    content = {
        "entries": [
            {"path": "docs/test.md", "title": "Test Doc"}
        ]
    }
    registry_file.write_text(json.dumps(content), encoding="utf-8")
    registry = load_registry(registry_file)
    assert len(registry) == 1
    assert registry[0]['path'] == 'docs/test.md'

def test_find_all_markdown_files(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    (docs_dir / "file1.md").write_text("content")
    (docs_dir / "file2.txt").write_text("content")
    sub_dir = docs_dir / "sub"
    sub_dir.mkdir()
    (sub_dir / "file3.md").write_text("content")
    
    found_files = find_all_markdown_files(docs_dir)
    found_files_posix = {Path(p).as_posix() for p in found_files}
    
    assert "docs/file1.md" in found_files_posix
    assert "docs/sub/file3.md" in found_files_posix
    assert "docs/file2.txt" not in found_files_posix

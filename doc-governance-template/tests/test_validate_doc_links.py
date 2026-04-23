import pytest
import os
from pathlib import Path
from unittest.mock import patch

from scripts.validate_doc_links import check_links, resolve_link, extract_links

def test_extract_links():
    content = "Here is a [link](some_file.md) and [another](http://example.com)."
    links = extract_links(content)
    assert links == ["some_file.md", "http://example.com"]

def test_resolve_link_infinite_symlink(tmp_path):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text("content")
    
    sym1 = tmp_path / "sym1.md"
    sym2 = tmp_path / "sym2.md"
    
    os.symlink(sym2, sym1)
    os.symlink(sym1, sym2)
    
    # Should handle RuntimeError from pathlib.resolve and return None
    resolved = resolve_link("sym1.md", doc_path)
    assert resolved is None

def test_check_links_broken_link(tmp_path):
    doc_path = tmp_path / "doc.md"
    doc_path.write_text("Link to [missing](missing.md)")

    with patch("scripts.validate_doc_links.get_docs_to_check", return_value=[doc_path]), \
         patch("scripts.validate_doc_links.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_links()
        assert failures == 1

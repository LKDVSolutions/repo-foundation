import pytest
from pathlib import Path
from scripts import aggregate_registry

def test_extract_governed_entries(tmp_path, monkeypatch):
    # Create a dummy repo structure
    repo_root = tmp_path
    docs_dir = repo_root / "docs"
    docs_dir.mkdir()
    
    # File with valid frontmatter
    doc1 = docs_dir / "doc1.md"
    doc1.write_text("---\ndoc_id: DOC1\ndoc_class: active\ntitle: Test Doc 1\n---\nContent here", encoding="utf-8")
    
    # File with no frontmatter
    doc2 = docs_dir / "doc2.md"
    doc2.write_text("# No frontmatter here", encoding="utf-8")
    
    # File with malformed frontmatter
    doc3 = docs_dir / "doc3.md"
    doc3.write_text("---\nmalformed yaml\n---\nContent", encoding="utf-8")
    
    # File in root
    doc4 = repo_root / "root_doc.md"
    doc4.write_text("---\ndoc_id: ROOT\ndoc_class: entrypoint\n---\n", encoding="utf-8")

    # Monkeypatch REPO_ROOT in the script
    monkeypatch.setattr(aggregate_registry, "REPO_ROOT", repo_root)
    
    entries = aggregate_registry.extract_governed_entries()
    
    assert len(entries) == 2
    doc_ids = [e["doc_id"] for e in entries]
    assert "DOC1" in doc_ids
    assert "ROOT" in doc_ids
    
    # Check paths
    for entry in entries:
        if entry["doc_id"] == "DOC1":
            assert entry["path"] == "docs/doc1.md"
        if entry["doc_id"] == "ROOT":
            assert entry["path"] == "root_doc.md"

def test_render_registry_md():
    entries = [
        {"doc_id": "ID1", "doc_class": "active", "title": "Title 1", "path": "path/1.md"},
        {"doc_id": "ID2", "doc_class": "generated", "title": "Title 2", "path": "path/2.md"}
    ]
    output = aggregate_registry.render_registry_md(entries)
    assert "# Documentation Registry" in output
    assert "ID1" in output
    assert "Title 2" in output
    assert "## Registry Table" in output
    assert "## Coverage Summary" in output

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch

from scripts import build_doc_registry_md

def test_load_registry_entries_valid(tmp_path):
    yaml_content = {"entries": [{"doc_id": "1", "doc_class": "active"}]}
    yaml_file = tmp_path / "DOC_REGISTRY.yaml"
    yaml_file.write_text(yaml.dump(yaml_content))
    
    with patch("scripts.build_doc_registry_md.REGISTRY_YAML", yaml_file):
        entries = build_doc_registry_md.load_registry_entries()
        assert len(entries) == 1
        assert entries[0]["doc_id"] == "1"

def test_load_registry_entries_malformed(tmp_path):
    # Malformed / empty roots should raise ValueError without crashing ungracefully
    yaml_file = tmp_path / "DOC_REGISTRY.yaml"
    
    # Empty file
    yaml_file.write_text("")
    with patch("scripts.build_doc_registry_md.REGISTRY_YAML", yaml_file):
        with pytest.raises(ValueError, match="must be a dictionary"):
            build_doc_registry_md.load_registry_entries()
            
    # List root
    yaml_file.write_text("- item1\n- item2")
    with patch("scripts.build_doc_registry_md.REGISTRY_YAML", yaml_file):
        with pytest.raises(ValueError, match="must be a dictionary"):
            build_doc_registry_md.load_registry_entries()
            
    # Missing entries
    yaml_file.write_text("other_key: value")
    with patch("scripts.build_doc_registry_md.REGISTRY_YAML", yaml_file):
        with pytest.raises(ValueError, match="'entries' missing or invalid"):
            build_doc_registry_md.load_registry_entries()

def test_render_registry_md():
    entries = [{"doc_id": "test_id", "doc_class": "active", "title": "Test Doc"}]
    output = build_doc_registry_md.render_registry_md(entries)
    assert "test_id" in output
    assert "Test Doc" in output
    assert "## Registry Table" in output

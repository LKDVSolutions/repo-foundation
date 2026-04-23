import pytest
from unittest.mock import patch
from pathlib import Path

from scripts import hydrate_context

def test_hydrate_context(tmp_path):
    context_file = tmp_path / ".agent_context.md"
    registry_yaml = tmp_path / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"
    registry_yaml.parent.mkdir(parents=True, exist_ok=True)
    registry_yaml.write_text("")
    
    with patch("scripts.hydrate_context.CONTEXT_FILE", context_file), \
         patch("scripts.hydrate_context.REPO_ROOT", tmp_path), \
         patch("sys.argv", ["hydrate_context.py"]):
        hydrate_context.main()
        
    assert context_file.exists()
    assert "Documentation Registry" in context_file.read_text()

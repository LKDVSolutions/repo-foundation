import pytest
from unittest.mock import patch
from pathlib import Path

from scripts import hydrate_context

def test_hydrate_context(tmp_path):
    context_file = tmp_path / ".agent_context.md"
    registry_cache = tmp_path / ".registry_cache.json"
    registry_cache.write_text('{"entries": []}', encoding="utf-8")
    
    with patch("scripts.hydrate_context.CONTEXT_FILE", context_file), \
         patch("scripts.hydrate_context.REPO_ROOT", tmp_path), \
         patch("sys.argv", ["hydrate_context.py"]):
        hydrate_context.main()
        
    assert context_file.exists()
    assert "Documentation Registry" in context_file.read_text()

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


def test_hydrate_context_rejects_invalid_github_ref(tmp_path):
    context_file = tmp_path / ".agent_context.md"
    registry_cache = tmp_path / ".registry_cache.json"
    registry_cache.write_text('{"entries": []}', encoding="utf-8")

    with patch("scripts.hydrate_context.CONTEXT_FILE", context_file), \
         patch("scripts.hydrate_context.REPO_ROOT", tmp_path), \
         patch("sys.argv", ["hydrate_context.py", "--github", "bad ref"]) :
        with pytest.raises(SystemExit) as exc:
            hydrate_context.main()

    assert exc.value.code == 1


def test_hydrate_context_accepts_valid_github_ref(tmp_path):
    context_file = tmp_path / ".agent_context.md"
    registry_cache = tmp_path / ".registry_cache.json"
    registry_cache.write_text('{"entries": []}', encoding="utf-8")

    with patch("scripts.hydrate_context.CONTEXT_FILE", context_file), \
         patch("scripts.hydrate_context.REPO_ROOT", tmp_path), \
         patch("scripts.hydrate_context.fetch_github_context", return_value="issue body") as fetch_mock, \
         patch("sys.argv", ["hydrate_context.py", "--github", "#123"]):
        hydrate_context.main()

    fetch_mock.assert_called_once_with("#123")
    assert "GitHub Context (#123)" in context_file.read_text(encoding="utf-8")

import pytest
from unittest.mock import patch

from scripts.check_doc_registry_sync import check_registry_sync

def test_check_registry_sync_success():
    with patch("scripts.check_doc_registry_sync.REGISTRY_YAML") as mock_yaml, \
         patch("scripts.check_doc_registry_sync.REGISTRY_MD") as mock_md, \
         patch("scripts.check_doc_registry_sync.load_registry_entries") as mock_load, \
         patch("scripts.check_doc_registry_sync.render_registry_md") as mock_render:
        
        mock_yaml.exists.return_value = True
        mock_md.exists.return_value = True
        mock_md.read_text.return_value = "rendered content"
        mock_render.return_value = "rendered content"
        
        passed, warnings, failures = check_registry_sync()
        assert failures == 0

def test_check_registry_sync_fail():
    with patch("scripts.check_doc_registry_sync.REGISTRY_YAML") as mock_yaml, \
         patch("scripts.check_doc_registry_sync.REGISTRY_MD") as mock_md, \
         patch("scripts.check_doc_registry_sync.load_registry_entries") as mock_load, \
         patch("scripts.check_doc_registry_sync.render_registry_md") as mock_render:
        
        mock_yaml.exists.return_value = True
        mock_md.exists.return_value = True
        mock_md.read_text.return_value = "old content"
        mock_render.return_value = "new content"
        
        passed, warnings, failures = check_registry_sync()
        assert failures == 1

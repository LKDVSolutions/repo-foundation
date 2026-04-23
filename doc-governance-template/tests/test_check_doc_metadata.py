import pytest
import yaml
from pathlib import Path
from unittest.mock import patch

from scripts.check_doc_metadata import check_metadata

def test_check_metadata_valid(tmp_path):
    yaml_content = {
        "entries": [
            {
                "doc_id": "doc1",
                "doc_class": "active",
                "authority_kind": "guide",
                "system_owner": "user1",
                "doc_owner": "user1",
                "updated_by": "user1",
                "authoritative_for": [],
                "refresh_policy": "none",
                "superseded_by": "doc2"
            },
            {
                "doc_id": "doc2",
                "doc_class": "historical",
            }
        ]
    }
    yaml_file = tmp_path / "DOC_REGISTRY.yaml"
    yaml_file.write_text(yaml.dump(yaml_content))
    
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_metadata()
        assert failures == 0

def test_check_metadata_cycle(tmp_path):
    yaml_content = {
        "entries": [
            {"doc_id": "doc1", "superseded_by": "doc2"},
            {"doc_id": "doc2", "superseded_by": "doc3"},
            {"doc_id": "doc3", "superseded_by": "doc1"},
        ]
    }
    yaml_file = tmp_path / "DOC_REGISTRY.yaml"
    yaml_file.write_text(yaml.dump(yaml_content))
    
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_metadata()
        assert failures > 0

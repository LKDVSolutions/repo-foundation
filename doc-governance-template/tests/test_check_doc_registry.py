import pytest
import yaml
import json
from pathlib import Path
from unittest.mock import patch

from scripts.check_doc_registry import check_registry

def test_check_registry_valid_schema(tmp_path):
    schema = {
        "type": "object",
        "properties": {
            "entries": {
                "type": "array",
                "items": {"type": "object", "properties": {"doc_id": {"type": "string"}}}
            }
        }
    }
    yaml_content = {"entries": [{"doc_id": "1"}, {"doc_id": "2"}]}
    
    schema_file = tmp_path / "schema.json"
    yaml_file = tmp_path / "registry.yaml"
    schema_file.write_text(json.dumps(schema))
    yaml_file.write_text(yaml.dump(yaml_content))
    
    with patch("scripts.check_doc_registry.SCHEMA_PATH", schema_file), \
         patch("scripts.check_doc_registry.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_registry.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_registry()
        assert failures == 0

def test_check_registry_invalid_schema(tmp_path):
    schema = {
        "type": "object",
        "properties": {
            "entries": {
                "type": "array",
                "items": {"type": "object", "required": ["doc_id"]}
            }
        }
    }
    yaml_content = {"entries": [{"other": "1"}]}
    
    schema_file = tmp_path / "schema.json"
    yaml_file = tmp_path / "registry.yaml"
    schema_file.write_text(json.dumps(schema))
    yaml_file.write_text(yaml.dump(yaml_content))
    
    with patch("scripts.check_doc_registry.SCHEMA_PATH", schema_file), \
         patch("scripts.check_doc_registry.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_registry.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_registry()
        assert failures > 0

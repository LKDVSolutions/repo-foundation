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


def test_check_registry_non_dict_fails(tmp_path):
    """Registry that parses to a non-dict should fail with a clear message."""
    registry_file = tmp_path / "registry.json"
    registry_file.write_text(json.dumps([{"doc_id": "doc1"}]))
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps({"type": "object"}))

    with patch("scripts.check_doc_registry.SCHEMA_PATH", schema_file), \
         patch("scripts.check_doc_registry.REGISTRY_PATH", registry_file), \
         patch("scripts.check_doc_registry.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_registry()
        assert failures > 0


def test_check_registry_yaml_null_fails(tmp_path):
    """Empty YAML registry (parses to None) should fail gracefully."""
    registry_file = tmp_path / "registry.yaml"
    registry_file.write_text("")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps({"type": "object"}))

    with patch("scripts.check_doc_registry.SCHEMA_PATH", schema_file), \
         patch("scripts.check_doc_registry.REGISTRY_PATH", registry_file), \
         patch("scripts.check_doc_registry.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_registry()
        assert failures > 0


def test_check_registry_parse_error_message(tmp_path, capsys):
    """Error messages should reflect the actual error type, not always 'JSON parse error'."""
    registry_file = tmp_path / "registry.yaml"
    registry_file.write_text("{ unclosed: [bad\n  : }")
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps({"type": "object"}))

    with patch("scripts.check_doc_registry.SCHEMA_PATH", schema_file), \
         patch("scripts.check_doc_registry.REGISTRY_PATH", registry_file), \
         patch("scripts.check_doc_registry.REPO_ROOT", tmp_path):
        passed, warnings, failures = check_registry()
    captured = capsys.readouterr()
    assert failures > 0
    assert "JSON parse error" not in captured.out


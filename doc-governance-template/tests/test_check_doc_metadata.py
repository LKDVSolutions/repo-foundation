import pytest
import json
import yaml
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from scripts.check_doc_metadata import check_metadata


def _write_registry(tmp_path, entries):
    yaml_file = tmp_path / "DOC_REGISTRY.yaml"
    yaml_file.write_text(yaml.dump({"entries": entries}))
    return yaml_file


def _patch(tmp_path, yaml_file):
    return patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
           patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
           patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml")


# --- existing tests (preserved) ---

def test_check_metadata_valid(tmp_path):
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "authority_kind": "guide",
            "system_owner": "user1",
            "doc_owner": "user1",
            "updated_by": "user1",
            "authoritative_for": [],
            "refresh_policy": "none",
            "superseded_by": "doc2",
        },
        {"doc_id": "doc2", "doc_class": "historical"},
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures == 0


def test_check_metadata_cycle(tmp_path):
    yaml_file = _write_registry(tmp_path, [
        {"doc_id": "doc1", "superseded_by": "doc2"},
        {"doc_id": "doc2", "superseded_by": "doc3"},
        {"doc_id": "doc3", "superseded_by": "doc1"},
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures > 0


# --- new tests ---

def test_sentinel_title_fails(tmp_path):
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "title": "FIXME-NEEDS-TITLE",
            "authority_kind": "guide",
            "system_owner": "u",
            "doc_owner": "u",
            "updated_by": "u",
            "authoritative_for": [],
            "refresh_policy": "manual",
        }
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures > 0


def test_sentinel_title_passes_when_real_title(tmp_path):
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "title": "Real Title",
            "authority_kind": "guide",
            "system_owner": "u",
            "doc_owner": "u",
            "updated_by": "u",
            "authoritative_for": [],
            "refresh_policy": "manual",
        }
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures == 0


def test_staleness_fail_on_old_last_verified(tmp_path):
    old_date = (date.today() - timedelta(days=45)).isoformat()
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "authority_kind": "runtime_evidence",
            "system_owner": "u",
            "doc_owner": "u",
            "updated_by": "u",
            "authoritative_for": [],
            "refresh_policy": "manual",
            "source_inputs": ["some/path.md"],
            "verification_level": "ssh_verified",
            "last_verified": old_date,
        }
    ])
    # Create the source_inputs file so that check passes
    (tmp_path / "some").mkdir()
    (tmp_path / "some" / "path.md").write_text("content")
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures > 0  # 45d > 30d fail threshold for runtime_evidence


def test_staleness_warn_on_moderately_old(tmp_path):
    warn_date = (date.today() - timedelta(days=10)).isoformat()
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "authority_kind": "runtime_evidence",
            "system_owner": "u",
            "doc_owner": "u",
            "updated_by": "u",
            "authoritative_for": [],
            "refresh_policy": "manual",
            "source_inputs": ["some/path.md"],
            "verification_level": "ssh_verified",
            "last_verified": warn_date,
        }
    ])
    (tmp_path / "some").mkdir()
    (tmp_path / "some" / "path.md").write_text("content")
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, warnings, failures = check_metadata()
        assert failures == 0  # 10d > 7d warn, but < 30d fail
        assert warnings > 0


def test_staleness_pass_on_fresh(tmp_path):
    fresh_date = date.today().isoformat()
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "authority_kind": "runtime_evidence",
            "system_owner": "u",
            "doc_owner": "u",
            "updated_by": "u",
            "authoritative_for": [],
            "refresh_policy": "manual",
            "source_inputs": ["some/path.md"],
            "verification_level": "ssh_verified",
            "last_verified": fresh_date,
        }
    ])
    (tmp_path / "some").mkdir()
    (tmp_path / "some" / "path.md").write_text("content")
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, warnings, failures = check_metadata()
        assert failures == 0
        assert warnings == 0


def test_source_inputs_missing_path_fails(tmp_path):
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "authority_kind": "current_config",
            "system_owner": "u",
            "doc_owner": "u",
            "updated_by": "u",
            "authoritative_for": [],
            "refresh_policy": "manual",
            "source_inputs": ["does/not/exist.yaml"],
            "verification_level": "repo_derived",
        }
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures > 0


def test_source_inputs_existing_path_passes(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "thing.py").write_text("# ok")
    yaml_file = _write_registry(tmp_path, [
        {
            "doc_id": "doc1",
            "doc_class": "active",
            "authority_kind": "current_config",
            "system_owner": "u",
            "doc_owner": "u",
            "updated_by": "u",
            "authoritative_for": [],
            "refresh_policy": "manual",
            "source_inputs": ["scripts/thing.py"],
            "verification_level": "repo_derived",
        }
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures == 0


def test_depends_on_cycle_fails(tmp_path):
    yaml_file = _write_registry(tmp_path, [
        {"doc_id": "A", "doc_class": "historical", "depends_on": ["B"]},
        {"doc_id": "B", "doc_class": "historical", "depends_on": ["A"]},
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures > 0


def test_depends_on_no_cycle_passes(tmp_path):
    # Use historical class (not governed) so other metadata checks don't fire
    yaml_file = _write_registry(tmp_path, [
        {"doc_id": "A", "doc_class": "historical", "depends_on": ["B"]},
        {"doc_id": "B", "doc_class": "historical", "depends_on": []},
    ])
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", yaml_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures == 0


def test_registry_non_dict_fails(tmp_path):
    """Registry that parses to a non-dict (e.g. a list) should emit a clear FAIL."""
    registry_file = tmp_path / "registry.json"
    registry_file.write_text(json.dumps([{"doc_id": "doc1"}]))
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", registry_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures > 0


def test_registry_yaml_null_fails(tmp_path):
    """Registry YAML that parses to None (empty file) should emit a clear FAIL."""
    registry_file = tmp_path / "registry.yaml"
    registry_file.write_text("")
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", registry_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
        assert failures > 0


def test_registry_yaml_parse_error_message(tmp_path, capsys):
    """YAML parse failure should report a YAML-specific error, not JSON parse error."""
    registry_file = tmp_path / "registry.yaml"
    # JSON parse will fail; YAML parse will also fail on this content
    registry_file.write_text("{ unclosed: [bad yaml\n  : }")
    with patch("scripts.check_doc_metadata.REGISTRY_PATH", registry_file), \
         patch("scripts.check_doc_metadata.REPO_ROOT", tmp_path), \
         patch("scripts.check_doc_metadata.AGENT_CONFIG_PATH", tmp_path / "nonexistent.yaml"):
        _, _, failures = check_metadata()
    captured = capsys.readouterr()
    assert failures > 0
    assert "JSON parse error" not in captured.out
    assert "YAML" in captured.out or "parse error" in captured.out.lower()


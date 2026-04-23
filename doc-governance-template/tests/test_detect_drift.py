import pytest
from unittest.mock import patch
from pathlib import Path

from scripts.detect_drift import check_docker_compose_drift

def test_check_docker_compose_drift_detected(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    blueprint_file = tmp_path / "docs" / "reference" / "architecture.md"
    blueprint_file.parent.mkdir(parents=True)
    
    compose_file.write_text("services:\n  web: ...")
    blueprint_file.write_text("No services described here.")
    
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift.log_drift") as mock_log, \
         patch("scripts.detect_drift.draft_pr_for_drift") as mock_pr:
        
        check_docker_compose_drift()
        
        mock_log.assert_called_once()
        mock_pr.assert_called_once()

def test_check_docker_compose_drift_not_detected(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    blueprint_file = tmp_path / "docs" / "reference" / "architecture.md"
    blueprint_file.parent.mkdir(parents=True)
    
    compose_file.write_text("services:\n  web: ...")
    blueprint_file.write_text("We have services:\n  web: ...")
    
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift.log_drift") as mock_log, \
         patch("scripts.detect_drift.draft_pr_for_drift") as mock_pr:
        
        check_docker_compose_drift()
        
        mock_log.assert_not_called()
        mock_pr.assert_not_called()

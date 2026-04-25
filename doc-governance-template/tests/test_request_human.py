import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import os

from scripts.request_human import request_human

def test_request_human_uses_repo_root_path_from_any_cwd(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    needs_attention_file = repo_root / "docs" / "plans" / "NEEDS_ATTENTION.md"

    outside_cwd = tmp_path / "outside"
    outside_cwd.mkdir()
    current_dir = os.getcwd()
    os.chdir(outside_cwd)

    try:
        with patch("scripts.request_human.REPO_ROOT", repo_root), \
             patch("subprocess.run") as mock_run, \
             patch("sys.exit") as mock_exit:

            mock_proc = MagicMock()
            mock_proc.stdout = "diff output"
            mock_run.return_value = mock_proc

            request_human("Please help")

            mock_exit.assert_called_once_with(1)

            assert needs_attention_file.exists()
            content = needs_attention_file.read_text()
            assert "**AGENT REQUEST**: Please help" in content
            assert "diff output" in content
            assert not (outside_cwd / "docs" / "plans" / "NEEDS_ATTENTION.md").exists()
    finally:
        os.chdir(current_dir)

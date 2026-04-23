import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from scripts.request_human import request_human

def test_request_human(tmp_path):
    needs_attention_file = tmp_path / "docs" / "plans" / "NEEDS_ATTENTION.md"
    needs_attention_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Needs to mock Path to control where needs_attention_file points.
    # Since request_human.py defines needs_attention_file = Path("docs/plans/NEEDS_ATTENTION.md")
    # we can change the working directory or mock it.
    
    import os
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        with patch("subprocess.run") as mock_run, \
             patch("sys.exit") as mock_exit:
             
            mock_proc = MagicMock()
            mock_proc.stdout = "diff output"
            mock_run.return_value = mock_proc
            
            request_human("Please help")
            
            mock_exit.assert_called_once_with(1)
            
            actual_file = tmp_path / "docs" / "plans" / "NEEDS_ATTENTION.md"
            assert actual_file.exists()
            content = actual_file.read_text()
            assert "**AGENT REQUEST**: Please help" in content
            assert "diff output" in content
    finally:
        os.chdir(current_dir)

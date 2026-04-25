import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

from scripts.init_project import replace_placeholders, generate_boot_instruction

def test_replace_placeholders(tmp_path):
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello [YOUR-PROJECT-NAME]")
        
        replace_placeholders("MyProject", "Alice", "My project description")
        
        assert test_file.read_text() == "Hello MyProject"
    finally:
        os.chdir(current_dir)

def test_generate_boot_instruction(tmp_path):
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        boot_file = generate_boot_instruction("blank")
        assert boot_file.exists()
        assert "Blank Canvas" in boot_file.read_text()
    finally:
        os.chdir(current_dir)


def test_main_orchestrates_bootstrap_flow(tmp_path):
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        with patch(
            "builtins.input",
            side_effect=["MyProject", "Alice", "A useful description", "1"],
        ), patch("scripts.init_project.subprocess.run") as run_mock:
            from scripts import init_project

            init_project.main()

        run_mock.assert_called_once_with([sys.executable, "scripts/aggregate_registry.py"], check=True)
        boot_file = tmp_path / ".gemini" / "boot_instruction.md"
        assert boot_file.exists()
    finally:
        os.chdir(current_dir)

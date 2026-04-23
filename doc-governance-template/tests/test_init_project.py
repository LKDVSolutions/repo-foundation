import pytest
import os
from pathlib import Path

from scripts.init_project import replace_placeholders, generate_boot_instruction

def test_replace_placeholders(tmp_path):
    current_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        test_file = tmp_path / "test.md"
        test_file.write_text("Hello [YOUR-PROJECT-NAME]")
        
        replace_placeholders("MyProject", "Alice")
        
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

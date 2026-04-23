import pytest
from io import StringIO
import sys

from scripts.generate_tree import generate_tree

def test_generate_tree(tmp_path):
    (tmp_path / "folder1").mkdir()
    (tmp_path / "folder1" / "file1.txt").write_text("test")
    (tmp_path / "file2.txt").write_text("test")
    (tmp_path / ".git").mkdir() # Should be ignored
    
    captured_output = StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured_output
    
    try:
        generate_tree(str(tmp_path))
    finally:
        sys.stdout = original_stdout
        
    output = captured_output.getvalue()
    
    assert "folder1" in output
    assert "file1.txt" in output
    assert "file2.txt" in output
    assert ".git" not in output

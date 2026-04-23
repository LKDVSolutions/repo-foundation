import pytest
from unittest.mock import patch

from scripts.docs_gate import run_gate

def test_run_gate_fast():
    with patch("scripts.docs_gate.check_registry", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_metadata", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_registry_sync", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_links") as mock_links:
        
        exit_code = run_gate(fast=True)
        assert exit_code == 0
        mock_links.assert_not_called()

def test_run_gate_full():
    with patch("scripts.docs_gate.check_registry", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_metadata", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_registry_sync", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_links", return_value=(1, 0, 1)):
        
        exit_code = run_gate(fast=False)
        assert exit_code == 1

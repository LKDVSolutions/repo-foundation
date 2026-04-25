import pytest
from unittest.mock import patch

from scripts.docs_gate import run_gate

def test_run_gate_fast():
    with patch("scripts.docs_gate.check_registry", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_metadata", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_registry_sync", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_evidence_freshness", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_shell_scripts", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.LOGGER.log"), \
         patch("scripts.docs_gate.check_links") as mock_links:
        
        exit_code = run_gate(fast=True)
        assert exit_code == 0
        mock_links.assert_not_called()

def test_run_gate_full():
    with patch("scripts.docs_gate.check_registry", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_metadata", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_registry_sync", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_evidence_freshness", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.check_shell_scripts", return_value=(1, 0, 0)), \
         patch("scripts.docs_gate.LOGGER.log"), \
         patch("scripts.docs_gate.check_links", return_value=(1, 0, 1)):
        
        exit_code = run_gate(fast=False)
        assert exit_code == 1


def test_run_gate_continues_after_check_exception():
    call_order = []

    def failing_check():
        call_order.append("registry")
        raise PermissionError("denied")

    def succeeding_check(name):
        def _inner():
            call_order.append(name)
            return (1, 0, 0)
        return _inner

    with patch("scripts.docs_gate.check_registry", side_effect=failing_check), \
         patch("scripts.docs_gate.check_metadata", side_effect=succeeding_check("metadata")), \
         patch("scripts.docs_gate.check_registry_sync", side_effect=succeeding_check("sync")), \
         patch("scripts.docs_gate.check_evidence_freshness", side_effect=succeeding_check("evidence")), \
         patch("scripts.docs_gate.check_shell_scripts", side_effect=succeeding_check("shell")), \
         patch("scripts.docs_gate.LOGGER.log") as log_mock:
        exit_code = run_gate(fast=True)

    assert call_order == ["registry", "metadata", "sync", "evidence", "shell"]
    assert exit_code == 1
    assert any(call.args[1] == "check_exception" for call in log_mock.call_args_list if len(call.args) >= 2)

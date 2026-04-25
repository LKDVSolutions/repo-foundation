import json

from scripts.governance_logger import AUDIT_TRAIL_PATH, GovernanceLogger


def test_governance_logger_writes_jsonl(tmp_path):
    audit_path = tmp_path / ".runtime" / "AGENT_AUDIT_TRAIL.jsonl"
    logger = GovernanceLogger(script="unit-test", audit_path=audit_path)

    logger.log("INFO", "event_name", "hello", doc_id="DOC_1")

    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    payload = json.loads(lines[0])
    assert payload["level"] == "INFO"
    assert payload["script"] == "unit-test"
    assert payload["event"] == "event_name"
    assert payload["doc_id"] == "DOC_1"
    assert payload["message"] == "hello"
    assert "timestamp" in payload


def test_default_audit_trail_path_is_runtime_local():
    assert AUDIT_TRAIL_PATH.parts[-2:] == (".runtime", "AGENT_AUDIT_TRAIL.jsonl")

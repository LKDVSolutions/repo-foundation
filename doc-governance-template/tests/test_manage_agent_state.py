import yaml
from unittest.mock import patch
from scripts import manage_agent_state

def _write_state(tmp_path, content: str):
    target = tmp_path / "AGENT_STATE.md"
    target.write_text(content, encoding="utf-8")
    return target

def test_update_status_updates_frontmatter(tmp_path):
    path = _write_state(
        tmp_path,
        "---\ndoc_id: AGENT_STATE\nagent_state:\n  status: In Progress\n  blockers: []\n---\n",
    )

    with patch("scripts.manage_agent_state.AGENT_STATE_PATH", path), patch("scripts.manage_agent_state.LOGGER.log"):
        assert manage_agent_state.update_agent_state("Blocked")

    content = path.read_text(encoding="utf-8")
    fm = yaml.safe_load(content.split("---")[1])
    assert fm["agent_state"]["status"] == "Blocked"
    assert "- **Current Status**: Blocked" in content

def test_update_blocker_appends_to_frontmatter_list(tmp_path):
    path = _write_state(
        tmp_path,
        "---\ndoc_id: AGENT_STATE\nagent_state:\n  status: In Progress\n  blockers: [\"old\"]\n---\n",
    )

    with patch("scripts.manage_agent_state.AGENT_STATE_PATH", path), patch("scripts.manage_agent_state.LOGGER.log"):
        assert manage_agent_state.update_agent_state("In Progress", "new")

    content = path.read_text(encoding="utf-8")
    fm = yaml.safe_load(content.split("---")[1])
    assert "old" in fm["agent_state"]["blockers"]
    assert "new" in fm["agent_state"]["blockers"]
    assert "- old" in content
    assert "- new" in content

def test_missing_file_returns_false(tmp_path):
    path = tmp_path / "missing.md"
    with patch("scripts.manage_agent_state.AGENT_STATE_PATH", path), patch("scripts.manage_agent_state.LOGGER.log"):
        assert not manage_agent_state.update_agent_state("Idle")

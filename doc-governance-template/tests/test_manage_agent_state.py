from unittest.mock import patch

from scripts import manage_agent_state


def _write_state(tmp_path, content: str):
    target = tmp_path / "AGENT_STATE.md"
    target.write_text(content, encoding="utf-8")
    return target


def test_update_status_replaces_line(tmp_path):
    path = _write_state(
        tmp_path,
        "---\ntype: template\n---\n\n## Current Task\n- **Status**: In Progress\n",
    )

    with patch("scripts.manage_agent_state.AGENT_STATE_PATH", path), patch("scripts.manage_agent_state.LOGGER.log"):
        assert manage_agent_state.update_agent_state("Blocked")

    content = path.read_text(encoding="utf-8")
    assert "- **Status**: Blocked" in content


def test_update_blocker_updates_checkbox_in_section(tmp_path):
    path = _write_state(
        tmp_path,
        "---\ntype: template\n---\n\n## Blockers / Issues\n- [ ] old blocker\n\n## Next Steps\n- [ ] x\n",
    )

    with patch("scripts.manage_agent_state.AGENT_STATE_PATH", path), patch("scripts.manage_agent_state.LOGGER.log"):
        assert manage_agent_state.update_agent_state("In Progress", "new blocker")

    content = path.read_text(encoding="utf-8")
    assert "- [ ] new blocker" in content
    assert "- [ ] old blocker" not in content


def test_update_blocker_adds_section_if_missing(tmp_path):
    path = _write_state(tmp_path, "---\ntype: template\n---\n\n## Current Task\n- **Status**: In Progress\n")

    with patch("scripts.manage_agent_state.AGENT_STATE_PATH", path), patch("scripts.manage_agent_state.LOGGER.log"):
        assert manage_agent_state.update_agent_state("In Progress", "needs dependency")

    content = path.read_text(encoding="utf-8")
    assert "## Blockers / Issues" in content
    assert "- [ ] needs dependency" in content


def test_missing_file_returns_false(tmp_path):
    path = tmp_path / "missing.md"
    with patch("scripts.manage_agent_state.AGENT_STATE_PATH", path), patch("scripts.manage_agent_state.LOGGER.log"):
        assert not manage_agent_state.update_agent_state("Idle")

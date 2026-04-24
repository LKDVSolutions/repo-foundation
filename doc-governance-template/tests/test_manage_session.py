from pathlib import Path
from unittest.mock import patch

from scripts.manage_session import create_session, resume_session


def _session_files(tmp_path: Path):
    sessions_dir = tmp_path / "docs" / "history"
    lock_path = sessions_dir / "SESSION_ENVELOPES.lock"
    return sessions_dir, lock_path


def test_create_session_writes_envelope(tmp_path):
    sessions_dir, lock_path = _session_files(tmp_path)

    with patch("scripts.manage_session.REPO_ROOT", tmp_path), \
         patch("scripts.manage_session.SESSIONS_DIR", sessions_dir), \
         patch("scripts.manage_session.SESSION_LOCK", lock_path), \
         patch("scripts.manage_session.LOGGER.log"):
        code = create_session(
            parent_task_id="TASK-1",
            active_files=["scripts/detect_drift.py"],
            checkpoint_summary="Implemented adapters",
            git_diff_sha="abc123",
            resume_target_file="scripts/detect_drift.py",
            resume_target_line=42,
        )

    assert code == 0
    created = list(sessions_dir.glob("SESSION_*.md"))
    assert len(created) == 1
    content = created[0].read_text(encoding="utf-8")
    assert "parent_task_id: TASK-1" in content
    assert "resume_target_file: scripts/detect_drift.py" in content
    assert "resume_target_line: 42" in content


def test_resume_session_returns_error_when_missing(tmp_path):
    sessions_dir, lock_path = _session_files(tmp_path)
    sessions_dir.mkdir(parents=True)

    with patch("scripts.manage_session.REPO_ROOT", tmp_path), \
         patch("scripts.manage_session.SESSIONS_DIR", sessions_dir), \
         patch("scripts.manage_session.SESSION_LOCK", lock_path), \
         patch("scripts.manage_session.LOGGER.log"):
        code = resume_session("session-20260424-0101-abcdef")

    assert code == 1


def test_resume_session_reads_checkpoint(tmp_path):
    sessions_dir, lock_path = _session_files(tmp_path)
    sessions_dir.mkdir(parents=True)
    session_id = "session-20260424-0202-abcdef"
    path = sessions_dir / f"SESSION_{session_id}.md"
    path.write_text(
        """---
doc_id: SESSION_dummy
doc_class: active
authority_kind: current_config
title: Session Envelope
primary_audience: agents
task_entry_for: []
system_owner: documentation-governance
doc_owner: system-wide
updated_by: auto
authoritative_for: []
source_inputs: []
refresh_policy: auto
verification_level: repo_derived
status: active
depends_on: []
---
# Session Envelope

## Checkpoint
- checkpoint_summary: Continue from parser fixes
- resume_target_file: scripts/detect_drift.py
- resume_target_line: 123
""",
        encoding="utf-8",
    )

    with patch("scripts.manage_session.REPO_ROOT", tmp_path), \
         patch("scripts.manage_session.SESSIONS_DIR", sessions_dir), \
         patch("scripts.manage_session.SESSION_LOCK", lock_path), \
         patch("scripts.manage_session.LOGGER.log") as mock_log:
        code = resume_session(session_id)

    assert code == 0
    assert mock_log.called

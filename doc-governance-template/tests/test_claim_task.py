"""Tests for scripts/claim_task.py — multi-agent file claim protocol."""
import time
from pathlib import Path

import pytest

from scripts.claim_task import ClaimManager, ClaimError


def test_claim_file_writes_entry(tmp_path):
    claims_file = tmp_path / "AGENT_CLAIMS.md"
    mgr = ClaimManager(claims_file=claims_file)
    mgr.claim("docs/foo.md", agent_id="agent-A", ttl_seconds=300)

    content = claims_file.read_text()
    assert "docs/foo.md" in content
    assert "agent-A" in content


def test_double_claim_raises(tmp_path):
    claims_file = tmp_path / "AGENT_CLAIMS.md"
    mgr = ClaimManager(claims_file=claims_file)
    mgr.claim("docs/foo.md", agent_id="agent-A", ttl_seconds=300)

    with pytest.raises(ClaimError, match="already claimed"):
        mgr.claim("docs/foo.md", agent_id="agent-B", ttl_seconds=300)


def test_release_removes_entry(tmp_path):
    claims_file = tmp_path / "AGENT_CLAIMS.md"
    mgr = ClaimManager(claims_file=claims_file)
    mgr.claim("docs/foo.md", agent_id="agent-A", ttl_seconds=300)
    mgr.release("docs/foo.md", agent_id="agent-A")

    content = claims_file.read_text()
    assert "docs/foo.md" not in content


def test_expired_claim_can_be_overridden(tmp_path):
    claims_file = tmp_path / "AGENT_CLAIMS.md"
    mgr = ClaimManager(claims_file=claims_file)
    mgr.claim("docs/foo.md", agent_id="agent-A", ttl_seconds=0)  # already expired
    time.sleep(0.01)
    mgr.claim("docs/foo.md", agent_id="agent-B", ttl_seconds=300)

    content = claims_file.read_text()
    assert "agent-B" in content


def test_cleanup_removes_expired(tmp_path):
    claims_file = tmp_path / "AGENT_CLAIMS.md"
    mgr = ClaimManager(claims_file=claims_file)
    mgr.claim("docs/foo.md", agent_id="agent-A", ttl_seconds=0)
    time.sleep(0.01)
    removed = mgr.cleanup()

    assert removed == 1
    content = claims_file.read_text()
    assert "docs/foo.md" not in content


def test_check_returns_none_when_free(tmp_path):
    claims_file = tmp_path / "AGENT_CLAIMS.md"
    mgr = ClaimManager(claims_file=claims_file)
    assert mgr.check("docs/foo.md") is None


def test_check_returns_claim_info_when_claimed(tmp_path):
    claims_file = tmp_path / "AGENT_CLAIMS.md"
    mgr = ClaimManager(claims_file=claims_file)
    mgr.claim("docs/foo.md", agent_id="agent-A", ttl_seconds=300)
    info = mgr.check("docs/foo.md")

    assert info is not None
    assert info["agent_id"] == "agent-A"

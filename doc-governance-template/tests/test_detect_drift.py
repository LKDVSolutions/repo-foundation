import pytest
from unittest.mock import patch
from pathlib import Path

from scripts.detect_drift import (
    DockerComposeAdapter,
    DriftReport,
    log_drift,
    extract_governance_block,
    main,
)


# --- existing tests (preserved) ---

def test_docker_compose_adapter_detects_undocumented_service(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("services:\n  web:\n    image: nginx\n  db:\n    image: postgres\n")

    blueprint_file = tmp_path / "docs" / "architecture" / "OVERVIEW.md"
    blueprint_file.parent.mkdir(parents=True)
    blueprint_file.write_text("# Architecture\n## Services\n- web\n")

    adapter = DockerComposeAdapter()
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path):
        report = adapter.check()

    assert report is not None
    assert report.has_drift
    assert "db" in report.undocumented
    assert "web" not in report.undocumented


def test_docker_compose_adapter_no_drift(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("services:\n  web:\n    image: nginx\n")

    blueprint_file = tmp_path / "docs" / "architecture" / "OVERVIEW.md"
    blueprint_file.parent.mkdir(parents=True)
    blueprint_file.write_text("# Architecture\n## Services\n- web\n")

    adapter = DockerComposeAdapter()
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path):
        report = adapter.check()

    assert report is not None
    assert not report.has_drift


def test_docker_compose_adapter_skips_when_no_source(tmp_path):
    adapter = DockerComposeAdapter()
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path):
        result = adapter.check()
    assert result is None


def test_docker_compose_adapter_warns_when_no_blueprint(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("services:\n  web:\n    image: nginx\n")

    adapter = DockerComposeAdapter()
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path):
        result = adapter.check()
    assert result is None


def test_log_drift_appends_to_inbox(tmp_path):
    inbox = tmp_path / "IDEA_INBOX.md"
    inbox.write_text("# Idea Inbox\n\n")

    with patch("scripts.detect_drift.IDEA_INBOX", inbox):
        log_drift("test service X not documented")

    content = inbox.read_text()
    assert "test service X not documented" in content


def test_log_drift_does_not_duplicate(tmp_path):
    inbox = tmp_path / "IDEA_INBOX.md"
    inbox.write_text("# Idea Inbox\n\n")

    with patch("scripts.detect_drift.IDEA_INBOX", inbox):
        log_drift("duplicate message")
        log_drift("duplicate message")

    content = inbox.read_text()
    assert content.count("duplicate message") == 1


# --- new tests ---

def test_main_returns_1_on_drift(tmp_path):
    """detect_drift.main() must return 1 (not 0) when drift is present."""
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("services:\n  web:\n    image: nginx\n  db:\n    image: postgres\n")

    blueprint_file = tmp_path / "docs" / "architecture" / "OVERVIEW.md"
    blueprint_file.parent.mkdir(parents=True)
    # Only 'web' documented — 'db' is undocumented drift
    blueprint_file.write_text("# Architecture\n## Services\n- web\n")

    inbox = tmp_path / "docs" / "plans" / "IDEA_INBOX.md"
    inbox.parent.mkdir(parents=True)
    inbox.write_text("# Idea Inbox\n\n")

    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift.IDEA_INBOX", inbox), \
         patch("scripts.detect_drift.create_github_issue"):
        exit_code = main()

    assert exit_code == 1


def test_main_returns_0_when_no_drift(tmp_path):
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text("services:\n  web:\n    image: nginx\n")

    blueprint_file = tmp_path / "docs" / "architecture" / "OVERVIEW.md"
    blueprint_file.parent.mkdir(parents=True)
    blueprint_file.write_text("# Architecture\n## Services\n- web\n")

    inbox = tmp_path / "docs" / "plans" / "IDEA_INBOX.md"
    inbox.parent.mkdir(parents=True)
    inbox.write_text("# Idea Inbox\n\n")

    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift.IDEA_INBOX", inbox):
        exit_code = main()

    assert exit_code == 0


# --- structured comment block parser tests ---

def test_extract_governance_block_structured_comment():
    content = "# Overview\n\n<!-- governance:services\nweb\ndb\nworker\n-->\n"
    items = extract_governance_block(content, "services")
    assert set(items) == {"web", "db", "worker"}


def test_extract_governance_block_ignores_other_kinds():
    content = "<!-- governance:ports\n80\n443\n-->\n<!-- governance:services\nweb\n-->\n"
    items = extract_governance_block(content, "services")
    assert items == ["web"]


def test_extract_governance_block_falls_back_to_prose_h2(tmp_path):
    content = "# Doc\n## Services\n- alpha\n- beta\n\n## Other\n- ignored\n"
    items = extract_governance_block(content, "services")
    assert "alpha" in items
    assert "beta" in items
    assert "ignored" not in items


def test_extract_governance_block_falls_back_to_prose_h3():
    content = "# Doc\n### Services\n- gamma\n\n### Other\n- skip\n"
    items = extract_governance_block(content, "services")
    assert "gamma" in items
    assert "skip" not in items


def test_extract_governance_block_falls_back_to_prose_table():
    content = "# Doc\n## Services\n| Service | Role |\n|---|---|\n| cache | Redis |\n"
    items = extract_governance_block(content, "services")
    assert "cache" in items


def test_extract_governance_block_empty_when_no_match():
    content = "# Doc\n\nNo services section here.\n"
    items = extract_governance_block(content, "services")
    assert items == []

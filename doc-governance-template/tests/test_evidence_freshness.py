"""Tests for evidence freshness checking in detect_drift.py."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.detect_drift import check_evidence_freshness


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _runtime_evidence_doc(tmp_path: Path, timestamp_str: str) -> Path:
    doc = tmp_path / "docs" / "reference" / "current" / "RUNTIME_STATUS.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(
        f"""\
---
doc_id: RUNTIME_STATUS
doc_class: active
authority_kind: runtime_evidence
title: Runtime Status
status: active
system_owner: engineering
doc_owner: '[YOUR-NAME]'
updated_by: human
---
# Runtime Status

Service is up.

```yaml governance:evidence
- host: "10.0.0.1"
  command: "docker ps"
  timestamp: "{timestamp_str}"
  output: "running"
  confidence: verified
```
""",
        encoding="utf-8",
    )
    return doc


FAKE_CONFIG = {
    "governance": {
        "staleness_ttl": {
            "runtime_evidence": {"warn_days": 7, "fail_days": 30}
        }
    }
}


def test_fresh_evidence_passes(tmp_path):
    now = datetime.now(tz=timezone.utc)
    _runtime_evidence_doc(tmp_path, _iso(now - timedelta(days=1)))
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift._load_agent_config", return_value=FAKE_CONFIG):
        passed, warned, failed = check_evidence_freshness()
    assert passed == 1
    assert warned == 0
    assert failed == 0


def test_stale_evidence_warns(tmp_path):
    now = datetime.now(tz=timezone.utc)
    _runtime_evidence_doc(tmp_path, _iso(now - timedelta(days=10)))
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift._load_agent_config", return_value=FAKE_CONFIG):
        passed, warned, failed = check_evidence_freshness()
    assert warned == 1
    assert failed == 0


def test_very_stale_evidence_fails(tmp_path):
    now = datetime.now(tz=timezone.utc)
    _runtime_evidence_doc(tmp_path, _iso(now - timedelta(days=35)))
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift._load_agent_config", return_value=FAKE_CONFIG):
        passed, warned, failed = check_evidence_freshness()
    assert failed == 1


def test_runtime_evidence_doc_with_no_block_warns(tmp_path):
    doc = tmp_path / "docs" / "reference" / "current" / "RUNTIME_STATUS.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(
        """\
---
doc_id: RUNTIME_STATUS
doc_class: active
authority_kind: runtime_evidence
title: Runtime Status
status: active
system_owner: engineering
doc_owner: '[YOUR-NAME]'
updated_by: human
---
# Runtime Status

Service is up. (no structured evidence block)
""",
        encoding="utf-8",
    )
    with patch("scripts.detect_drift.REPO_ROOT", tmp_path), \
         patch("scripts.detect_drift._load_agent_config", return_value=FAKE_CONFIG):
        passed, warned, failed = check_evidence_freshness()
    assert warned == 1

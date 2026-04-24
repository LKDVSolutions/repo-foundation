# Governance Features 02–06 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add sprint-planning prompt, architecture-review prompt, dependency-update prompt, multi-agent claim protocol, and machine-readable evidence format to the doc-governance-template.

**Architecture:** FEATURE-02/03/04 are pure Markdown additions (prompt templates + PROMPT_INDEX.md update). FEATURE-05 adds a FileLock-based claim/reservation script and a governed claims file. FEATURE-06 defines a structured `evidence:` YAML block convention and wires freshness checking into `detect_drift.py` and `docs_gate.py`.

**Tech Stack:** Python 3.12, `filelock`, `yaml`, `marko`, `pytest`, existing `scripts/` patterns.

---

## File Map

| Status | Path | Feature | Responsibility |
|--------|------|---------|----------------|
| **Create** | `docs/plans/prompts/PROMPT_SPRINT_PLANNING.md` | F-02 | Sprint planning prompt template |
| **Create** | `docs/plans/prompts/PROMPT_ARCHITECTURE_REVIEW.md` | F-03 | Pre-implementation architecture review prompt |
| **Create** | `docs/plans/prompts/PROMPT_DEPENDENCY_UPDATE.md` | F-04 | Safe dependency upgrade proposal prompt |
| **Create** | `scripts/claim_task.py` | F-05 | CLI: claim / release / check / cleanup file locks |
| **Create** | `docs/history/AGENT_CLAIMS.md` | F-05 | Machine-readable active claim registry |
| **Create** | `tests/test_claim_task.py` | F-05 | Unit tests for claim_task.py |
| **Create** | `tests/test_evidence_freshness.py` | F-06 | Unit tests for evidence freshness checker |
| **Modify** | `docs/plans/prompts/PROMPT_INDEX.md` | F-02/03/04 | Add three new prompt rows to the table |
| **Modify** | `docs/development/ENGINEERING_STANDARDS.md` | F-05 | Update §5 Guardrails with claim_task.py rule |
| **Modify** | `AGENTS.md` | F-05 | Add §5 — Claim Protocol (one paragraph) |
| **Modify** | `CLAUDE.md` | F-06 | Extend §2 Evidence Standard with structured YAML block |
| **Modify** | `GEMINI.md` | F-06 | Same extension (§2 is identical) |
| **Modify** | `scripts/detect_drift.py` | F-06 | Add `check_evidence_freshness()` function |
| **Modify** | `scripts/docs_gate.py` | F-06 | Import and run evidence freshness check in fast gate |

---

## Task 1: FEATURE-02/03/04 — Prompt Templates

**Files:**
- Create: `docs/plans/prompts/PROMPT_SPRINT_PLANNING.md`
- Create: `docs/plans/prompts/PROMPT_ARCHITECTURE_REVIEW.md`
- Create: `docs/plans/prompts/PROMPT_DEPENDENCY_UPDATE.md`
- Modify: `docs/plans/prompts/PROMPT_INDEX.md`

- [ ] **Step 1.1: Create PROMPT_SPRINT_PLANNING.md**

```markdown
---
doc_id: PROMPT_SPRINT_PLANNING
doc_class: active
authority_kind: guide
title: 'Prompt Template: Sprint Planning'
primary_audience: humans
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for: []
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
**Directive**: You are working in: `[PROJECT_ROOT_PATH]`

Your mission is to produce a structured sprint plan for the upcoming sprint by reading the current governance artifacts and proposing a realistic, prioritized work package.

**CRITICAL RULE:** Do NOT assume sprint state from memory. Read the current files directly.

**Phase 1: Current-State Ingestion**
Read the following files in order and extract their current state:
1. `docs/plans/[SPRINT_TRACKER.md]` — identify the most recently completed sprint number and its velocity (points completed vs committed).
2. `docs/plans/[EPIC_TRACKER.md]` — identify all in-progress and next-up epics with their priorities.
3. `docs/plans/[SCOPE_BOARD.md]` — identify all items in `Ready` status and their estimated effort.

**Phase 2: Capacity Calculation**
1. Calculate available capacity: `[TEAM_SIZE] × [SPRINT_DAYS] × [HOURS_PER_DAY] = total_hours`. Convert to points using the project's velocity ratio from Phase 1.
2. Identify carry-over items from the previous sprint (incomplete items with dependencies).
3. Subtract carry-over from available capacity to get net new capacity.

**Phase 3: Scope Proposal**
Select items from the `Ready` column of SCOPE_BOARD.md in priority order until net new capacity is consumed. Respect these rules:
- **No scope creep:** Do not pull items not in `Ready` status.
- **Epic alignment:** Prefer items that advance an in-progress epic over starting a new one.
- **Risk buffer:** Reserve 15% of capacity as an unplanned work buffer.

**Phase 4: Sprint Plan Output**
Produce the following structured output:
```
## Sprint [N+1] Plan

**Capacity:** [X] points
**Carry-over:** [list items]
**Committed Scope:**
| Item ID | Title | Epic | Points | Owner |
|---------|-------|------|--------|-------|
| ...     | ...   | ...  | ...    | ...   |

**Risk Buffer:** [Y] points reserved

**Success Criteria:**
- [ ] [Item 1 done condition]
- [ ] [Item 2 done condition]
```

**Mandatory Validation:**
Run `python scripts/docs_gate.py --fast` to ensure your actions did not break the documentation registry.
```

- [ ] **Step 1.2: Create PROMPT_ARCHITECTURE_REVIEW.md**

```markdown
---
doc_id: PROMPT_ARCHITECTURE_REVIEW
doc_class: active
authority_kind: guide
title: 'Prompt Template: Architecture Review'
primary_audience: both
task_entry_for:
- implement_change
- architectural_decision
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for: []
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
**Directive**: You are the **Architecture Review Officer** for this change. Your goal is NOT to begin implementation. Your goal is to surface architectural risks, constraints, and decision points BEFORE any code is written.

Proposed change: `[DESCRIBE THE CHANGE IN ONE SENTENCE]`

**CRITICAL RULE:** Do not write any implementation code during this review. If you identify a clear, unambiguous path forward, document it in a decision record — do not execute it.

**Phase 1: Dependency & Interface Mapping**
Read the relevant architecture and current-config docs:
1. `docs/architecture/OVERVIEW.md` — identify which services/modules are involved.
2. `docs/reference/current/SERVICE_INVENTORY.md` — confirm current deployment state of affected services.
3. Any blueprint docs (`authority_kind: blueprint`) related to the affected subsystem.

Answer these questions explicitly:
- What are the upstream callers of the component being changed?
- What are the downstream dependencies (services, DBs, queues) it writes to?
- Does this change affect any public API contract (HTTP, event schema, DB schema)?

**Phase 2: Risk Assessment**
For each of the following risk vectors, state: **Applies / Does Not Apply / Uncertain** and explain why:
1. **Data migration risk** — will this change require a schema change or data backfill?
2. **Backwards-compatibility risk** — will existing callers break if deployed without a coordinated rollout?
3. **Concurrency risk** — does this change introduce or affect any shared mutable state?
4. **Observability gap** — are there metrics, logs, or traces that will no longer be valid post-change?
5. **Blast radius** — if this change fails at runtime, what is the worst-case impact?

**Phase 3: Decision Record Draft**
If the review reveals a significant design choice (e.g., "we must add an idempotency key" or "we must version the API"), draft a new entry for `docs/history/DECISION_LOG.md`:
```
## Decision: [Title]
**Date:** [YYYY-MM-DD]
**Context:** [Why this decision is needed]
**Decision:** [What was decided]
**Consequences:** [What this enables or forecloses]
```

**Phase 4: Go / No-Go Gate**
State one of:
- **GO:** No blocking risks. Proceed with implementation plan.
- **CONDITIONAL GO:** Proceed only after [specific pre-condition].
- **NO-GO:** [Specific blocking risk that must be resolved first].

**Mandatory Validation:**
Run `python scripts/docs_gate.py --fast` after any file changes.
```

- [ ] **Step 1.3: Create PROMPT_DEPENDENCY_UPDATE.md**

```markdown
---
doc_id: PROMPT_DEPENDENCY_UPDATE
doc_class: active
authority_kind: guide
title: 'Prompt Template: Dependency Update'
primary_audience: humans
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for: []
refresh_policy: manual
verification_level: none
status: active
depends_on:
- PROMPT_DEPENDENCY_BOOTSTRAP
---
**Directive**: You are working in: `[PROJECT_ROOT_PATH]`

Your mission is to produce a safe, live-verified dependency upgrade proposal. You MUST NOT apply any changes directly — output a proposal that a human will review and apply via `propose_fixes.py`.

**CRITICAL RULE:** Do NOT rely on your training data for package versions. All versions must be live-queried from the package registry. Your training data is outdated.

**Phase 1: Current State Extraction**
Read the pinned versions from the current lockfile(s):
- Python: read `requirements.txt` or `requirements-dev.txt` (or `pyproject.toml` `[tool.poetry.dependencies]`)
- Node: read `package-lock.json` (`packages[""].dependencies`)
- Other: `[LOCKFILE_PATH]`

List each pinned package and its current version in this format:
```
| Package | Pinned Version | Source File |
|---------|---------------|-------------|
| fastapi | 0.109.0       | requirements.txt |
```

**Phase 2: Live Registry Query**
For each package, query the live registry for the latest stable version.
- Python: `pip index versions [package] 2>&1 | grep "Available versions" | head -1`
- Node: `npm view [package] version`
- Do NOT query pre-release or RC versions unless the project is already on a pre-release track.

Mark each package as:
- **UP_TO_DATE** — pinned == latest
- **PATCH_AVAILABLE** — same major.minor, higher patch (safe to update)
- **MINOR_AVAILABLE** — same major, higher minor (review changelog)
- **MAJOR_AVAILABLE** — higher major (requires migration assessment)

**Phase 3: Changelog Review (for MINOR and MAJOR)**
For any package with MINOR_AVAILABLE or MAJOR_AVAILABLE, fetch the changelog or release notes and identify:
1. Any breaking changes in the API this project uses.
2. Any new security advisories (CVEs).

**Phase 4: Upgrade Proposal via propose_fixes.py**
Run `python scripts/propose_fixes.py --report` to confirm the current patch state.

Then produce upgrade recommendations in this format:
```
## Upgrade Proposal

### Safe (PATCH) — Apply without review
| Package | From | To | Risk |
|---------|------|----|------|
| ...     | ...  | ...| low  |

### Review Required (MINOR)
| Package | From | To | Breaking Change? | Action |
|---------|------|----|-----------------|--------|
| ...     | ...  | ...| no              | update |

### Defer (MAJOR)
| Package | From | To | Migration Notes |
|---------|------|----|-----------------|
| ...     | ...  | ...| [link to guide] |
```

**Mandatory Validation:**
After human applies any upgrade, run:
1. The project's test suite.
2. `python scripts/docs_gate.py --fast`
```

- [ ] **Step 1.4: Update PROMPT_INDEX.md — add three rows to the Available Prompts table**

Find the closing `| **QA Gate Review** | ...` row and add after it:

```markdown
| **Sprint Planning** | [PROMPT_SPRINT_PLANNING.md](PROMPT_SPRINT_PLANNING.md) | Produce a structured sprint plan from SPRINT_TRACKER, EPIC_TRACKER, and SCOPE_BOARD |
| **Architecture Review** | [PROMPT_ARCHITECTURE_REVIEW.md](PROMPT_ARCHITECTURE_REVIEW.md) | Pre-implementation SDL-style architecture risk review before writing code |
| **Dependency Update** | [PROMPT_DEPENDENCY_UPDATE.md](PROMPT_DEPENDENCY_UPDATE.md) | Live-verified dependency upgrade proposal using propose_fixes.py |
```

- [ ] **Step 1.5: Run docs gate**

```bash
cd /path/to/repo && python scripts/aggregate_registry.py && python scripts/docs_gate.py --fast
```

Expected: `Gate: PASS` with 3 new docs registered.

- [ ] **Step 1.6: Commit**

```bash
git add docs/plans/prompts/PROMPT_SPRINT_PLANNING.md \
        docs/plans/prompts/PROMPT_ARCHITECTURE_REVIEW.md \
        docs/plans/prompts/PROMPT_DEPENDENCY_UPDATE.md \
        docs/plans/prompts/PROMPT_INDEX.md \
        .registry_cache.json \
        docs/reference/registry/DOC_REGISTRY.md
git commit -m "feat(prompts): add sprint planning, architecture review, and dependency update prompts (F-02/03/04)"
```

---

## Task 2: FEATURE-05 — claim_task.py Script

**Files:**
- Create: `scripts/claim_task.py`
- Create: `tests/test_claim_task.py`

- [ ] **Step 2.1: Write the failing test**

Create `tests/test_claim_task.py`:

```python
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
```

- [ ] **Step 2.2: Run test to verify it fails**

```bash
pytest tests/test_claim_task.py -v
```

Expected: `ImportError: cannot import name 'ClaimManager' from 'scripts.claim_task'` (file does not exist yet).

- [ ] **Step 2.3: Create scripts/claim_task.py**

```python
#!/usr/bin/env python3
"""Multi-agent file claim protocol.

Prevents two agents from writing conflicting patches to the same target file.
Uses a FileLock over the full read-modify-write cycle on AGENT_CLAIMS.md.

Usage:
    python scripts/claim_task.py claim <file_path> [--agent-id <id>] [--ttl <seconds>]
    python scripts/claim_task.py release <file_path> [--agent-id <id>]
    python scripts/claim_task.py check <file_path>
    python scripts/claim_task.py cleanup
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from filelock import FileLock, Timeout

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CLAIMS_FILE = REPO_ROOT / "docs" / "history" / "AGENT_CLAIMS.md"
DEFAULT_TTL = 1800  # 30 minutes
LOCK_TIMEOUT = 30

_BLOCK_RE = re.compile(r"```yaml claims\n(.*?)```", re.DOTALL)

CLAIMS_HEADER = """\
---
doc_id: AGENT_CLAIMS
doc_class: active
authority_kind: current_config
title: Agent Claims Registry
primary_audience: agents
task_entry_for: []
system_owner: system-wide
doc_owner: '[YOUR-NAME]'
updated_by: auto
authoritative_for:
- active agent file reservations
refresh_policy: auto
verification_level: none
status: active
depends_on: []
---
# Agent Claims Registry

<!-- AUTO-MANAGED by scripts/claim_task.py — do not edit manually -->

```yaml claims
[]
```
"""


class ClaimError(RuntimeError):
    pass


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


class ClaimManager:
    def __init__(self, claims_file: Path = DEFAULT_CLAIMS_FILE) -> None:
        self.claims_file = claims_file
        self.lock_file = claims_file.with_suffix(".lock")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_claims(self) -> list[dict]:
        if not self.claims_file.exists():
            self.claims_file.parent.mkdir(parents=True, exist_ok=True)
            self.claims_file.write_text(CLAIMS_HEADER, encoding="utf-8")
        content = self.claims_file.read_text(encoding="utf-8")
        m = _BLOCK_RE.search(content)
        if not m:
            return []
        return yaml.safe_load(m.group(1)) or []

    def _write_claims(self, claims: list[dict]) -> None:
        if not self.claims_file.exists():
            self.claims_file.parent.mkdir(parents=True, exist_ok=True)
            self.claims_file.write_text(CLAIMS_HEADER, encoding="utf-8")
        content = self.claims_file.read_text(encoding="utf-8")
        block = "```yaml claims\n" + yaml.dump(claims, default_flow_style=False) + "```"
        new_content, count = _BLOCK_RE.subn(block, content)
        if count == 0:
            new_content = content.rstrip() + "\n\n" + block + "\n"
        self.claims_file.write_text(new_content, encoding="utf-8")

    def _active_claims(self, claims: list[dict]) -> list[dict]:
        now = _now()
        return [c for c in claims if _parse(c["expires_at"]) > now]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def claim(self, file_path: str, agent_id: str, ttl_seconds: int = DEFAULT_TTL) -> None:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            claims = self._active_claims(self._read_claims())
            for c in claims:
                if c["file"] == file_path:
                    raise ClaimError(
                        f"File '{file_path}' is already claimed by '{c['agent_id']}' "
                        f"until {c['expires_at']}"
                    )
            now = _now()
            expires = datetime.fromtimestamp(
                now.timestamp() + ttl_seconds, tz=timezone.utc
            )
            claims.append(
                {
                    "file": file_path,
                    "agent_id": agent_id,
                    "claimed_at": _iso(now),
                    "expires_at": _iso(expires),
                }
            )
            self._write_claims(claims)

    def release(self, file_path: str, agent_id: str) -> None:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            claims = self._read_claims()
            before = len(claims)
            claims = [
                c for c in claims
                if not (c["file"] == file_path and c["agent_id"] == agent_id)
            ]
            if len(claims) == before:
                print(f"  [WARN] No active claim found for '{file_path}' by '{agent_id}'")
            self._write_claims(claims)

    def check(self, file_path: str) -> dict | None:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            active = self._active_claims(self._read_claims())
            for c in active:
                if c["file"] == file_path:
                    return c
            return None

    def cleanup(self) -> int:
        with FileLock(str(self.lock_file), timeout=LOCK_TIMEOUT):
            claims = self._read_claims()
            active = self._active_claims(claims)
            removed = len(claims) - len(active)
            self._write_claims(active)
            return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-agent file claim protocol.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_claim = sub.add_parser("claim", help="Claim a file for exclusive editing.")
    p_claim.add_argument("file_path")
    p_claim.add_argument("--agent-id", default="anonymous")
    p_claim.add_argument("--ttl", type=int, default=DEFAULT_TTL)

    p_release = sub.add_parser("release", help="Release a claim.")
    p_release.add_argument("file_path")
    p_release.add_argument("--agent-id", default="anonymous")

    p_check = sub.add_parser("check", help="Check if a file is claimed.")
    p_check.add_argument("file_path")

    sub.add_parser("cleanup", help="Remove expired claims.")

    args = parser.parse_args()
    mgr = ClaimManager()

    if args.command == "claim":
        try:
            mgr.claim(args.file_path, agent_id=args.agent_id, ttl_seconds=args.ttl)
            print(f"  [OK] Claimed '{args.file_path}' for agent '{args.agent_id}'.")
            return 0
        except ClaimError as e:
            print(f"  [FAIL] {e}")
            return 1

    if args.command == "release":
        mgr.release(args.file_path, agent_id=args.agent_id)
        print(f"  [OK] Released '{args.file_path}'.")
        return 0

    if args.command == "check":
        info = mgr.check(args.file_path)
        if info:
            print(f"  [CLAIMED] '{args.file_path}' — agent '{info['agent_id']}' until {info['expires_at']}")
            return 1
        print(f"  [FREE] '{args.file_path}' is not claimed.")
        return 0

    if args.command == "cleanup":
        removed = mgr.cleanup()
        print(f"  [OK] Removed {removed} expired claim(s).")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2.4: Run tests to verify they pass**

```bash
pytest tests/test_claim_task.py -v
```

Expected: `7 passed` (all green).

- [ ] **Step 2.5: Commit**

```bash
git add scripts/claim_task.py tests/test_claim_task.py
git commit -m "feat(F-05): add claim_task.py multi-agent file reservation script"
```

---

## Task 3: FEATURE-05 — Claims File + Doc Updates

**Files:**
- Create: `docs/history/AGENT_CLAIMS.md`
- Modify: `docs/development/ENGINEERING_STANDARDS.md` (§5 Guardrails)
- Modify: `AGENTS.md` (add §5 Claim Protocol)

- [ ] **Step 3.1: Create docs/history/AGENT_CLAIMS.md**

```markdown
---
doc_id: AGENT_CLAIMS
doc_class: active
authority_kind: current_config
title: Agent Claims Registry
primary_audience: agents
task_entry_for: []
system_owner: system-wide
doc_owner: '[YOUR-NAME]'
updated_by: auto
authoritative_for:
- active agent file reservations
refresh_policy: auto
verification_level: none
status: active
depends_on: []
---
# Agent Claims Registry

<!-- AUTO-MANAGED by scripts/claim_task.py — do not edit manually -->

```yaml claims
[]
```
```

- [ ] **Step 3.2: Update ENGINEERING_STANDARDS.md §5 Guardrails**

In `docs/development/ENGINEERING_STANDARDS.md`, find the `**Guardrails:**` bullet list under `## 5. Agent Concurrency Model` and add a new bullet after the existing three:

```markdown
- **Claim before write:** Any agent that will mutate a file in a **non-idempotent** way (e.g., appending a patch to `.shadow/`, modifying `docs/history/`) MUST run `python scripts/claim_task.py claim <file_path> --agent-id <id>` before starting and `release` after. Check first with `python scripts/claim_task.py check <file_path>` — if claimed, wait or abort.
```

- [ ] **Step 3.3: Update AGENTS.md — add §5 Claim Protocol**

Append after the existing final section in `AGENTS.md`:

```markdown

## 5. Multi-Agent Claim Protocol

Before mutating any file that multiple agents could write concurrently (patch files in `.shadow/`, append-only history files, `docs/history/`), you MUST reserve it:

```bash
# Check if free
python scripts/claim_task.py check docs/history/DECISION_LOG.md

# Claim for up to 30 minutes
python scripts/claim_task.py claim docs/history/DECISION_LOG.md --agent-id [YOUR-SESSION-ID] --ttl 1800

# Release when done
python scripts/claim_task.py release docs/history/DECISION_LOG.md --agent-id [YOUR-SESSION-ID]
```

If `check` returns `[CLAIMED]`, **do not proceed**. Write your intent to `docs/plans/NEEDS_ATTENTION.md` and stop.
```

- [ ] **Step 3.4: Run docs gate**

```bash
python scripts/aggregate_registry.py && python scripts/docs_gate.py --fast
```

Expected: `Gate: PASS` with AGENT_CLAIMS doc registered.

- [ ] **Step 3.5: Commit**

```bash
git add docs/history/AGENT_CLAIMS.md \
        docs/development/ENGINEERING_STANDARDS.md \
        AGENTS.md \
        .registry_cache.json \
        docs/reference/registry/DOC_REGISTRY.md
git commit -m "feat(F-05): add AGENT_CLAIMS.md and document claim protocol in AGENTS.md and ENGINEERING_STANDARDS"
```

---

## Task 4: FEATURE-06 — Structured Evidence Block Convention

**Files:**
- Modify: `CLAUDE.md` (§2 Evidence Standard)
- Modify: `GEMINI.md` (§2 Evidence Standard)

- [ ] **Step 4.1: Update CLAUDE.md §2 Evidence Standard**

In `CLAUDE.md`, find the `### Evidence Standard` section. Replace the existing bullet list with:

```markdown
### Evidence Standard

Every claim in a `runtime_evidence` doc must be backed by a structured evidence block. Place this fenced block immediately after the prose claim it supports:

~~~markdown
```yaml evidence
- host: "10.0.0.20"
  command: "docker ps --filter name=n8n"
  timestamp: "2026-04-24T18:00:00Z"
  output: "n8n   Up 2 hours"
  confidence: verified
```
~~~

**Required fields:** `host` (or `source_file` for local artifacts), `command`, `timestamp` (ISO-8601 UTC), `output` (brief), `confidence` (`verified` / `partial` / `unverified`).

Staleness thresholds come from `.agent_config.yaml` under `governance.staleness_ttl.runtime_evidence`. `detect_drift.py` and `docs_gate.py` enforce these automatically.

> Legacy free-form evidence prose is still accepted but will generate a `[WARN]` from `docs_gate.py`. Migrate on next refresh.
```

- [ ] **Step 4.2: Update GEMINI.md §2 Evidence Standard**

Apply the identical replacement in `GEMINI.md` (the `### Evidence Standard` section under `## 2. Documentation Governance (Mandatory)` is identical content — replace with the same block from Step 4.1).

- [ ] **Step 4.3: Run docs gate**

```bash
python scripts/docs_gate.py --fast
```

Expected: `Gate: PASS` (no structural changes, only prose updates).

- [ ] **Step 4.4: Commit**

```bash
git add CLAUDE.md GEMINI.md
git commit -m "docs(F-06): define structured evidence YAML block convention in CLAUDE.md and GEMINI.md"
```

---

## Task 5: FEATURE-06 — Evidence Freshness Checker

**Files:**
- Create: `tests/test_evidence_freshness.py`
- Modify: `scripts/detect_drift.py`
- Modify: `scripts/docs_gate.py`

- [ ] **Step 5.1: Write the failing test**

Create `tests/test_evidence_freshness.py`:

```python
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

```yaml evidence
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
```

- [ ] **Step 5.2: Run test to verify it fails**

```bash
pytest tests/test_evidence_freshness.py -v
```

Expected: `ImportError: cannot import name 'check_evidence_freshness' from 'scripts.detect_drift'`

- [ ] **Step 5.3: Add check_evidence_freshness() to scripts/detect_drift.py**

Add these imports at the top of `detect_drift.py` (after existing imports):

```python
import json
from datetime import datetime, timezone
```

Add these two new functions before the `main()` function in `scripts/detect_drift.py`:

```python
def _load_agent_config() -> dict:
    config_path = REPO_ROOT / ".agent_config.yaml"
    if not config_path.exists():
        return {}
    import yaml as _yaml
    return _yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def check_evidence_freshness() -> tuple[int, int, int]:
    """Check all runtime_evidence docs for structured evidence block freshness.

    Returns (passed, warned, failed).
    Warn threshold and fail threshold come from .agent_config.yaml.
    """
    print("=== check_evidence_freshness ===")
    config = _load_agent_config()
    ttl = (
        config.get("governance", {})
        .get("staleness_ttl", {})
        .get("runtime_evidence", {})
    )
    warn_days = ttl.get("warn_days", 7)
    fail_days = ttl.get("fail_days", 30)

    evidence_block_re = re.compile(r"```yaml evidence\n(.*?)```", re.DOTALL)
    frontmatter_re = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

    import yaml as _yaml

    passed = warned = failed = 0
    md_files = list(REPO_ROOT.glob("*.md")) + list(REPO_ROOT.glob("docs/**/*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        fm_match = frontmatter_re.match(content)
        if not fm_match:
            continue
        fm = _yaml.safe_load(fm_match.group(1)) or {}
        if fm.get("authority_kind") != "runtime_evidence":
            continue

        rel = md_file.relative_to(REPO_ROOT)
        blocks = evidence_block_re.findall(content)

        if not blocks:
            print(f"  [WARN] {rel}: runtime_evidence doc has no structured evidence block")
            warned += 1
            continue

        now = datetime.now(tz=timezone.utc)
        for block_text in blocks:
            try:
                entries = _yaml.safe_load(block_text) or []
            except Exception as e:
                print(f"  [WARN] {rel}: could not parse evidence block: {e}")
                warned += 1
                continue

            for entry in entries:
                ts_str = entry.get("timestamp", "")
                if not ts_str:
                    print(f"  [WARN] {rel}: evidence entry missing timestamp")
                    warned += 1
                    continue
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    print(f"  [WARN] {rel}: evidence entry has invalid timestamp '{ts_str}'")
                    warned += 1
                    continue

                age_days = (now - ts).days
                cmd = entry.get("command", "?")
                if age_days >= fail_days:
                    print(f"  [FAIL] {rel}: evidence '{cmd}' is {age_days}d old (fail threshold: {fail_days}d)")
                    failed += 1
                elif age_days >= warn_days:
                    print(f"  [WARN] {rel}: evidence '{cmd}' is {age_days}d old (warn threshold: {warn_days}d)")
                    warned += 1
                else:
                    print(f"  [PASS] {rel}: evidence '{cmd}' is {age_days}d old")
                    passed += 1

    if passed == 0 and warned == 0 and failed == 0:
        print("  [INFO] No runtime_evidence docs found.")

    return passed, warned, failed
```

- [ ] **Step 5.4: Run tests to verify they pass**

```bash
pytest tests/test_evidence_freshness.py -v
```

Expected: `4 passed`.

- [ ] **Step 5.5: Wire evidence check into docs_gate.py fast gate**

In `scripts/docs_gate.py`, add the import after the existing imports:

```python
from detect_drift import check_evidence_freshness
```

Then inside `run_gate()`, after the `check_registry_sync()` block and before the `if not fast:` block, add:

```python
    print()
    p, w, f = check_evidence_freshness()
    total_passed += p
    total_warnings += w
    total_failures += f
```

- [ ] **Step 5.6: Run the full test suite**

```bash
pytest --tb=short -q
```

Expected: all tests pass (the new tests plus the existing ones).

- [ ] **Step 5.7: Run docs gate end-to-end**

```bash
python scripts/aggregate_registry.py && python scripts/docs_gate.py --fast
```

Expected: `Gate: PASS`. Evidence check will show `[INFO] No runtime_evidence docs found.` since the template has none by default.

- [ ] **Step 5.8: Commit**

```bash
git add tests/test_evidence_freshness.py \
        scripts/detect_drift.py \
        scripts/docs_gate.py \
        .registry_cache.json \
        docs/reference/registry/DOC_REGISTRY.md
git commit -m "feat(F-06): add structured evidence block convention and freshness check in docs_gate"
```

---

## Minimal File Summary

**Net new files (7):**
| File | Why it exists |
|------|--------------|
| `docs/plans/prompts/PROMPT_SPRINT_PLANNING.md` | F-02: missing prompt |
| `docs/plans/prompts/PROMPT_ARCHITECTURE_REVIEW.md` | F-03: missing prompt |
| `docs/plans/prompts/PROMPT_DEPENDENCY_UPDATE.md` | F-04: missing prompt |
| `scripts/claim_task.py` | F-05: claim/release script |
| `docs/history/AGENT_CLAIMS.md` | F-05: live claims registry |
| `tests/test_claim_task.py` | F-05: unit tests |
| `tests/test_evidence_freshness.py` | F-06: unit tests |

**Files modified (7):**
`PROMPT_INDEX.md`, `ENGINEERING_STANDARDS.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `detect_drift.py`, `docs_gate.py`

**Files auto-updated by scripts (2):**
`.registry_cache.json`, `docs/reference/registry/DOC_REGISTRY.md`

**Total: 16 files touched across 5 features.**

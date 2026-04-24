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

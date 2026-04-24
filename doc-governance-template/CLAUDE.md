---
doc_id: CLAUDE_md
doc_class: active
authority_kind: guide
title: "CLAUDE.md \u2014 Agent Instruction Surface"
primary_audience: agents
task_entry_for:
- implement_change
- investigate_runtime_issue
- operate_or_release
- refresh_current_docs
system_owner: system-wide
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- agent operational guardrails
- source of truth architecture rules
- documentation governance rules
refresh_policy: manual
verification_level: none
status: active
notes: 'Agent instruction surface. Authoritative for behavioral rules. Mutable facts
  (IPs, ports, service health) belong in current_config or runtime_evidence docs,
  not here.

  '
depends_on: []
---
# CLAUDE.md — Claude-Specific Agent Guidelines

This file provides specialized guidance for Claude Code and other Claude-based agents. It supplements the core standards defined in `AGENTS.md`.

## 1. Claude-Specific Behaviors

- **Plan Mode for All PRs:** You MUST enter `plan` mode (or explicitly state your plan) before any non-trivial change. Do not act without a peer-reviewed plan.
- **Verification Loops:** Always run tests and type-checks BEFORE declaring a task "Done". If you hit a wall, summarize and hand off via `docs/plans/NEEDS_ATTENTION.md`.
- **Subagents for Exploration:** Use subagents for broad searches, data analysis, or speculative research to keep your primary context window lean and high-signal.
- **Reference the Registry:** Every doc-related change MUST be preceded by reading `docs/reference/registry/DOC_REGISTRY.yaml` to ensure sync.

## 2. Documentation Governance (Mandatory)

### Authority Surface Map
- `runtime_evidence` — live system verification (SSH output, monitoring, deploy evidence)
- `current_config` — source artifacts (YAML, compose files, schema files, config files)
- `blueprint` — intended design docs (architecture, API contracts, interface specs)
- `plan` — roadmap, decisions, sequencing documents
- `guide` — CLAUDE.md, AGENTS.md, operational guides (behavioral rules only)
- `entrypoint` — INDEX.md, README (routing only)

### Evidence Standard
Every claim in a `current_config` or `runtime_evidence` doc must have:
- host/IP or source file reference
- exact command used to derive the claim
- timestamp
- key output (brief)
- conclusion + confidence (`verified` / `partial` / `unverified`)

## 3. Mandatory Task Closure
After every change:
1. `python scripts/aggregate_registry.py`
2. `python scripts/check_doc_registry_sync.py`
3. `python scripts/docs_gate.py --fast`

### Closure Output Format
End every implementation task with:
```
### Task Closure Summary
- **changed_sources**: [files modified]
- **updated_blueprints**: [blueprint docs updated — or "none"]
- **updated_current_docs**: [current_config docs refreshed — or "none"]
- **updated_runtime_evidence**: [runtime_evidence docs updated — or "none"]
- **unresolved_drift**: [discrepancies left open]
- **follow_up_required**: [next tasks, missing docs to create]
```

## 4. Key Navigation
- **Task routing**: [`docs/INDEX.md`](docs/INDEX.md)
- **Authority map**: [`docs/REFERENCE.md`](docs/REFERENCE.md)
- **Agent task routing**: [`docs/development/AGENT_WORKFLOW.md`](docs/development/AGENT_WORKFLOW.md)
- **Registry**: [`docs/reference/registry/DOC_REGISTRY.yaml`](docs/reference/registry/DOC_REGISTRY.yaml)

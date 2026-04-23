---
doc_id: GEMINI_md
doc_class: active
authority_kind: guide
title: "GEMINI.md \u2014 Gemini-Specific Agent Guidelines"
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
- gemini-specific operational guardrails
- parallelism and context efficiency rules
refresh_policy: manual
status: active
depends_on: []
---
# GEMINI.md — Gemini-Specific Agent Guidelines

This file provides specialized guidance for Gemini CLI and other Gemini-based agents. It supplements the core standards defined in `AGENTS.md`.

## 1. Gemini-Specific Behaviors

- **Parallelism First:** Utilize parallel tool execution for independent tasks (e.g., searching, reading multiple files, running concurrent shell commands). Set `wait_for_previous: true` only when a strict dependency exists.
- **Context Efficiency:** Be surgical with `grep_search` and `read_file` line ranges. Do not dump entire files into context unless necessary. Use `context`, `before`, and `after` parameters to get only what is needed.
- **Explicit Rationale:** Provide a concise, one-sentence explanation before any tool call that modifies the system or codebase.
- **Subagent Delegation:** For high-volume or repetitive tasks (e.g., batch refactoring, exhaustive codebase analysis), delegate to the `generalist` or `codebase_investigator` subagents to keep the main history lean.

## 2. Documentation Governance (Mandatory)

### Authority Surface Map
- `runtime_evidence` — live system verification (SSH output, monitoring, deploy evidence)
- `current_config` — source artifacts (YAML, compose files, schema files, config files)
- `blueprint` — intended design docs (architecture, API contracts, interface specs)
- `plan` — roadmap, decisions, sequencing documents
- `guide` — GEMINI.md, AGENTS.md, operational guides (behavioral rules only)
- `entrypoint` — INDEX.md, README (routing only)

### Evidence Standard
Every claim in a `current_config` or `runtime_evidence` doc must have:
- host/IP or source file reference
- exact command used to derive the claim
- timestamp
- key output (brief)
- conclusion + confidence (`verified` / `partial` / `unverified`)

## 3. Mandatory Task Closure
After every documentation or codebase change:
1. `python scripts/build_doc_registry_md.py`
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

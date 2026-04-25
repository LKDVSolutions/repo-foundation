---
doc_id: GEMINI_md
doc_class: active
authority_kind: guide
title: "GEMINI.md \u2014 Gemini-Specific Agent Guidelines"
primary_audience: agents
task_entry_for: []
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

Every claim in a `runtime_evidence` doc must be backed by a structured evidence block. For `current_config` docs, the source file itself is the evidence anchor — cite the file path and field in prose. Place this fenced block immediately after the prose claim it supports:

```yaml governance:evidence
- host: "10.0.0.20"
  command: "docker ps --filter name=n8n"
  timestamp: "2026-04-24T18:00:00Z"
  output: "n8n   Up 2 hours"
  confidence: verified
```

**Required fields:** `host` (or `source_file` for local artifacts), `command`, `timestamp` (ISO-8601 UTC), `output` (brief), `confidence` (`verified` / `partial` / `unverified`).

Staleness thresholds are configured in `.agent_config.yaml` under `governance.staleness_ttl.runtime_evidence`. `detect_drift.py` and `docs_gate.py` enforce these automatically once the evidence freshness check is active.

> Legacy free-form evidence prose is still accepted but will generate a `[WARN]` from `docs_gate.py`. Migrate on next refresh.

## 3. Mandatory Task Closure
After every documentation or codebase change:
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
- **Registry view**: [`docs/reference/registry/DOC_REGISTRY.md`](docs/reference/registry/DOC_REGISTRY.md)
- **Registry cache**: `.registry_cache.json`

---
doc_id: INDEX_md
doc_class: entrypoint
title: "[YOUR-PROJECT-NAME] \u2014 Repository Index"
primary_audience: both
task_entry_for:
- implement_change
- investigate_runtime_issue
- refresh_current_docs
- update_plan_or_roadmap
- operate_or_release
- test_or_operate_dev_environment
read_sequence:
- implement_change:
  - CLAUDE_md
- investigate_runtime_issue:
  - AGENT_WORKFLOW_md
  - CLAUDE_md
- refresh_current_docs:
  - DOC_REGISTRY_YAML
  - REFERENCE_md
- update_plan_or_roadmap: []
- operate_or_release:
  - CLAUDE_md
- test_or_operate_dev_environment: []
system_owner: system-wide
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for: []
refresh_policy: manual
verification_level: none
status: active
notes: "Universal repo entrypoint. Navigation only \u2014 no mutable facts. All task\
  \ classes route through this doc first.\n"
depends_on: []
---
# [YOUR-PROJECT-NAME] — Repository Index

[YOUR-PROJECT-DESCRIPTION]

---

## Strategic Planning (Day 0)
Before writing code or defining architecture, you MUST run the **[Strategic Alignment & Challenge](plans/prompts/PROMPT_STRATEGIC_ALIGNMENT.md)** prompt. This forces a deep-dive into feasibility, ecosystem dependencies (versions, licenses, risks), and technical friction to ensure the foundation is sound.

---

## By Task

### implement_change
Making a source code or config change — new feature, schema change, config update.

Start at: [CLAUDE.md](../CLAUDE.md) for guardrails and dev workflow rules.
<!-- Add: then docs/ROADMAP.md for phase context, then your subsystem docs -->
Full route: [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md#task-class-implement_change)

### investigate_runtime_issue
Diagnosing a bug, service failure, or unexpected behavior in a deployed system.

Start at: [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md#task-class-investigate_runtime_issue) for conflict-resolution rules, then [CLAUDE.md](../CLAUDE.md) for service map.
Full route: [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md#task-class-investigate_runtime_issue)

### refresh_current_docs
Updating current-state docs (`current_config` or `runtime_evidence` surfaces) after a source artifact changes.

Start at: [docs/reference/registry/DOC_REGISTRY.yaml](reference/registry/DOC_REGISTRY.yaml) to identify which docs are affected, then [docs/REFERENCE.md](REFERENCE.md) for the authority surface map.
Full route: [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md#task-class-refresh_current_docs)

### update_plan_or_roadmap
Updating roadmap phases, work package plans, or governance planning documents.

Start at: your project's roadmap doc for phase state.
<!-- Add: then docs/ROADMAP.md -->
Full route: [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md#task-class-update_plan_or_roadmap)

### operate_or_release
Deploying, releasing, or operating a service — SSH commands, Docker operations, database migrations.

Start at: [CLAUDE.md](../CLAUDE.md) for operational guardrails.
Full route: [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md#task-class-operate_or_release)

### test_or_operate_dev_environment
Working against a non-production environment — bring-up, push, smoke-test, reseed, or validate integrations.

Start at: your dev environment guide, then service inventory for placement, then runtime status for verification evidence.
<!-- Add: then infra/dev/README.md or equivalent -->
Full route: [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md#task-class-test_or_operate_dev_environment)

---

## By Role

### Human operator
Start at your project's README for system context, then navigate to the relevant subsystem doc. For port/service placement questions, see [docs/REFERENCE.md](REFERENCE.md#authority-surface-map).

### Agent — implementation
Start at [docs/INDEX.md](INDEX.md) (here), navigate to the task class above, then follow [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md) for required read order and fallback rules. Always check [docs/REFERENCE.md](REFERENCE.md) before treating any mutable fact as current.

### Agent — audit or review
Start at [docs/reference/registry/DOC_REGISTRY.yaml](reference/registry/DOC_REGISTRY.yaml) for doc classification. Use [docs/REFERENCE.md](REFERENCE.md) for resolution chains.

---

## Key Governance Docs

| Document | Path | Purpose |
|---|---|---|
| CLAUDE.md | `CLAUDE.md` | Agent guardrails, operational rules — authoritative for behavior |
| Repository Index | `docs/INDEX.md` | This file — universal navigation entrypoint |
| Reference Map | `docs/REFERENCE.md` | "Where is the truth?" — authority surfaces and resolution chains |
| Agent Workflow | `docs/development/AGENT_WORKFLOW.md` | Normative task routing and read-order rules for agents |
| Agent Capabilities | `docs/development/AGENT_CAPABILITIES.md` | Permitted tools and execution environment |
| Needs Attention | `docs/plans/NEEDS_ATTENTION.md` | Human-Agent Handoff / Interrupt blockers |
| Documentation Registry | `docs/reference/registry/DOC_REGISTRY.yaml` | Canonical doc classification, routing, and ownership |
| Maintenance Guide | `docs/development/DOCUMENTATION_MAINTENANCE.md` | When and how to update governed docs |
| Release Checklist | `docs/development/RELEASE_CHECKLIST.md` | Pre-release documentation checks |

<!-- Add your project-specific docs to this table, e.g.:
| Roadmap | `docs/ROADMAP.md` | Phase-by-phase goals and sequencing |
| Service Inventory | `docs/reference/current/SERVICE_INVENTORY.md` | Config-derived service placement |
| System Runtime Status | `docs/reference/current/SYSTEM_RUNTIME_STATUS.md` | Evidence-backed service state |
-->

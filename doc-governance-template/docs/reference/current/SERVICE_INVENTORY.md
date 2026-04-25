---
doc_id: SERVICE_INVENTORY
doc_class: active
authority_kind: current_config
title: Service Inventory
primary_audience: both
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- inventory of automated governance scripts
source_inputs:
- scripts/
last_verified: 2026-04-25
verification_level: repo_derived
refresh_policy: on_source_change
status: active
depends_on: []
---
# Service Inventory — Documentation Governance Template

This document identifies the internal "services" (automated scripts) that govern this repository.

## Automation Services

| Service Name | Primary Entrypoint | Runtime Environment | Deployment Mechanism | Purpose |
|---|---|---|---|---|
| **Quality Gate** | `scripts/docs_gate.py` | Python 3.12 (CI/CD) | GitHub Actions / Makefile | Ensures repository integrity and compliance |
| **Dependency Advisory Gate** | `scripts/check_dependency_advisories.py` | Python 3.12 (CI/CD) | GitHub Actions (required status check) | Verifies the pinned Python manifest has no published advisories |
| **Drift Reconciler** | `scripts/detect_drift.py` | Python 3.12 (CI/CD) | GitHub Actions (required status check) | Identifies discrepancies between blueprints and artifacts; exits 1 on drift |
| **Self-Healing CLI** | `scripts/auto_fix.py` | Python 3.12 (Local/Agent) | Manual / Agent-invoked | Repairs common documentation failures; injects sentinel values that fail the gate until corrected |
| **Escalation Gate** | `scripts/check_needs_attention.py` | Python 3.12 (CI/CD) | GitHub Actions (required status check) | Fails CI if NEEDS_ATTENTION.md contains open `- [ ]` agent blockers |
| **Branch Policy Verifier (GitHub adapter)** | `scripts/verify_branch_protection.py` | Python 3.12 (Local/Agent) | Optional / Agent-invoked | Audits GitHub branch protection against the documented required-check baseline |
| **Context Hydration** | `scripts/hydrate_context.py` | Python 3.12 (Local/Agent) | Agent-invoked | Prepares project and external context for agents |
| **Registry Aggregator** | `scripts/aggregate_registry.py` | Python 3.12 (Local/Agent) | Makefile / Agent-invoked | Aggregates Markdown frontmatter into `.registry_cache.json` and `DOC_REGISTRY.md` |

## External Integrations

| Integration | Mechanism | Required Credentials | Purpose |
|---|---|---|---|
| **GitHub API** | `gh` CLI or PyGithub | `GITHUB_TOKEN` | Drift PR creation, external context hydration |
| **Jira API** | HTTP REST | `JIRA_API_TOKEN` | External context hydration (optional) |

## Development Environments

| Environment | Purpose | Access Mechanism | Path |
|---|---|---|---|
| **Local / Codespace**| Development and agentic execution | Terminal / IDE | `/home/gary/data/coding/repo-foundation/doc-governance-template/` |
| **CI/CD (GitHub)** | Automated enforcement | GitHub Actions Runner | [Project Actions URL] |

## Operational Constraints

- **Required default-branch policy outcome**: enforce checks equivalent to `doc-gate`, `drift-detection`, and `dependency-advisory` on the selected hosting platform.
- **Current repository implementation**: GitHub branch protection on `main` requires `doc-gate`, `drift-detection`, and `dependency-advisory`.
- **Governance audit trail location**: the versioned `docs/history/AGENT_AUDIT_TRAIL.jsonl` file is a stub only. Live runtime audit entries are written to the ignored `.runtime/AGENT_AUDIT_TRAIL.jsonl` path.
- **Supported concurrency ceiling**: Up to 10 concurrent agents per project using the current file-lock coordination model.
- **Reason**: Registry and state mutations are serialized through file locks; above 10 concurrent writers, timeout-driven operational friction becomes likely.
- **Escalation trigger**: If routine operation requires more than 10 concurrent agents, redesign the coordination model instead of raising the limit informally.

# Service Inventory — Documentation Governance Template

This document identifies the internal "services" (automated scripts) that govern this repository.

## Automation Services

| Service Name | Primary Entrypoint | Runtime Environment | Deployment Mechanism | Purpose |
|---|---|---|---|---|
| **Quality Gate** | `scripts/docs_gate.py` | Python 3.12 (CI/CD) | GitHub Actions / Makefile | Ensures repository integrity and compliance |
| **Drift Reconciler** | `scripts/detect_drift.py` | Python 3.12 (CI/CD) | GitHub Actions | Identifies discrepancies between blueprints and artifacts |
| **Self-Healing CLI** | `scripts/auto_fix.py` | Python 3.12 (Local/Agent) | Manual / Agent-invoked | Automatically repairs common documentation failures |
| **Context Hydration** | `scripts/hydrate_context.py` | Python 3.12 (Local/Agent) | Agent-invoked | Prepares project and external context for agents |
| **Registry Builder** | `scripts/build_doc_registry_md.py`| Python 3.12 (Local/Agent) | Makefile / Agent-invoked | Generates human-readable views of the documentation metadata |

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

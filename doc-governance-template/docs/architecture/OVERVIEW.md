---
doc_id: ARCH_OVERVIEW
doc_class: active
authority_kind: blueprint
title: Architecture Overview
primary_audience: both
task_entry_for:
- implement_change
- investigate_runtime_issue
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- project architecture summary
refresh_policy: manual
status: active
depends_on: []
---
# Architecture Overview — Documentation Governance Template

This document provides a high-level summary of the system architecture, primary components, and their interactions for this Documentation Governance Template.

## System Model

The system is designed as an "Agent OS" for documentation management. It operates as a set of recursive validation and self-healing tools that maintain a canonical registry of project documentation.

### Core Components

1.  **Documentation Registry (`DOC_REGISTRY.yaml`)**:
    The central data store (current_config) for all governed documentation. It defines document classification, authority levels, ownership, and verification state.
2.  **Automation Engine (`scripts/`)**:
    A suite of Python-based tools that execute governance logic.
    - **`docs_gate.py`**: The primary quality gate for ensuring registry and document integrity.
    - **`auto_fix.py` / `auto_fix_registry.py`**: Self-healing mechanisms that programmatically repair documentation failures. auto_fix injects sentinel values (`FIXME-NEEDS-TITLE`) that intentionally fail the gate until a human corrects them.
    - **`detect_drift.py`**: Proactive drift detection between source artifacts and documentation blueprints. Exits 1 on drift — this is a required CI status check.
    - **`check_needs_attention.py`**: Blocks CI merges when `docs/plans/NEEDS_ATTENTION.md` contains open `- [ ]` agent blockers.
    - **`cascade_staleness.py` / `auto_fix_registry.py`**: Registry mutation scripts. Both use a full read-modify-write FileLock to prevent concurrent-write data loss (see ENGINEERING_STANDARDS.md — Agent Concurrency Model).
3.  **Agent Context Layer**:
    - **`hydrate_context.py`**: Aggregates repository and external context for AI agent memory.
    - **`manage_agent_state.py`**: Tracks active agent tasks and blockers.
4.  **CI/CD Pipeline**:
    - **GitHub Actions**: Daily and push-triggered quality gates ensuring documentation doesn't rot over time.
    - Both `doc-gate` and `drift-detection` jobs are required status checks — PRs cannot merge if either fails.

## Data Flows

1.  **Registry Rendering**: Metadata flows from the canonical `DOC_REGISTRY.yaml` into a human-readable `DOC_REGISTRY.md` via `build_doc_registry_md.py`.
2.  **Validation Loop**: The Quality Gate (`docs_gate.py`) reads documentation files and the registry to verify links, metadata, and synchronization.
3.  **Drift Detection**: `detect_drift.py` compares intended architecture (blueprints) against actual configuration (e.g., `docker-compose.yml`) and logs discrepancies for resolution.
4.  **Verification**: Manual or automated verification updates the `last_verified` and `verification_level` fields in the registry, providing a confidence metric for agents.

## Design Principles

- **Authority Hierarchy**: Runtime evidence and source artifacts are prioritized over design blueprints and plans.
- **Agent-First**: Documentation is structured to be parsed and navigated by autonomous agents.
- **Fail Fast**: The Quality Gate is a mandatory blocker for all PRs and pushes.
- **Self-Healing**: Common failures (missing headers, stale links) should be fixed programmatically.

## Governed Infrastructure

The following services are documented and governed by the drift detection pipeline.

```yaml governance:services
web
db
worker
```


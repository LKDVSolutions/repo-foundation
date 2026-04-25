---
doc_id: ARCH_OVERVIEW
doc_class: active
authority_kind: blueprint
title: Architecture Overview
primary_audience: both
task_entry_for: []
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

1.  **Documentation Registry (Markdown Frontmatter + `.registry_cache.json`)**:
    The distributed source of truth for all governed documentation. Each doc carries its own metadata as YAML frontmatter. `aggregate_registry.py` aggregates these into `.registry_cache.json` (machine-readable) and `DOC_REGISTRY.md` (human-readable).
2.  **Automation Engine (`scripts/`)**:
    A suite of Python-based tools that execute governance logic.
    - **`docs_gate.py`**: The primary quality gate for ensuring registry and document integrity.
    - **`auto_fix.py`**: Self-healing mechanism that programmatically repairs limited documentation failures. It injects sentinel values (`FIXME-NEEDS-TITLE`) that intentionally fail the gate until a human corrects them.
    - **`check_dependency_advisories.py`**: Supply-chain verification wrapper that runs `pip-audit` against the pinned Python manifest used by CI.
    - **`detect_drift.py`**: Proactive drift detection between source artifacts and documentation blueprints. Exits 1 on drift — this is a required CI status check.
    - **`check_needs_attention.py`**: Blocks CI merges when `docs/plans/NEEDS_ATTENTION.md` contains open `- [ ]` agent blockers.
    - **`aggregate_registry.py`**: Regenerates `.registry_cache.json` and `DOC_REGISTRY.md` from governed frontmatter.
3.  **Agent Context Layer**:
    - **`hydrate_context.py`**: Aggregates repository and external context for AI agent memory.
    - **`manage_agent_state.py`**: Tracks active agent tasks and blockers.
4.  **CI/CD Pipeline**:
    - **Reference implementation**: GitHub Actions provides daily and push-triggered quality gates for this template repository.
    - The security outcome is provider-agnostic: the default branch should require checks equivalent to `doc-gate`, `drift-detection`, and `dependency-advisory` on whichever source-control platform the project uses.
    - `verify_branch_protection.py` is the GitHub adapter for that policy today. Unsupported providers fall back to manual verification until an adapter exists.

## Operational Limits

- **Concurrency ceiling:** The file-lock design is intentionally operated at no more than 10 concurrent agents per project.
- **Rationale:** Beyond that level, lock contention and timeout failures become likely enough to create operational friction even if data corruption is avoided.
- **Out-of-scope scaling:** Supporting more than 10 concurrent agents requires a different coordination design and is intentionally deferred until real demand exists.

## Data Flows

1.  **Registry Aggregation**: Metadata is read from each Markdown file's YAML frontmatter by `aggregate_registry.py`, which writes `.registry_cache.json` (machine-readable) and `DOC_REGISTRY.md` (human-readable). No central YAML file is required.
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


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
    - **`auto_fix.py` / `auto_fix_registry.py`**: Self-healing mechanisms that programmatically repair documentation failures.
    - **`detect_drift.py`**: Proactive drift detection between source artifacts and documentation blueprints.
3.  **Agent Context Layer**:
    - **`hydrate_context.py`**: Aggregates repository and external context for AI agent memory.
    - **`manage_agent_state.py`**: Tracks active agent tasks and blockers.
4.  **CI/CD Pipeline**:
    - **GitHub Actions**: Daily and push-triggered quality gates ensuring documentation doesn't rot over time.

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

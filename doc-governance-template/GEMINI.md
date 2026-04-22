# GEMINI.md

## Project Overview
This is a **Documentation Governance Template**, designed to be integrated into any software project to manage documentation authority, task-routing, and automated quality gates. It prevents "documentation drift" by maintaining a canonical registry of documentation, defining an authority hierarchy, and providing scripts to validate documentation integrity.

## Key Components
- **`docs/INDEX.md`**: Universal entrypoint for navigation, routing tasks to relevant documentation.
- **`docs/REFERENCE.md`**: Authority surface map, defining the priority of documentation sources (e.g., `runtime_evidence` > `current_config` > `blueprint`).
- **`docs/reference/registry/DOC_REGISTRY.yaml`**: The source of truth for all governed documentation, including metadata like `last_verified` and `verification_level`.
- **`scripts/`**: Automation suite for documentation maintenance.

## Automation & Governance
The framework provides an automated quality gate (`scripts/docs_gate.py`) that must be passed to ensure documentation consistency.

### Key Commands
- **Install dependencies:**
  ```bash
  pip install pyyaml
  ```
- **Generate Registry Markdown:**
  ```bash
  python scripts/build_doc_registry_md.py
  ```
- **Validate Documentation (Fast Gate):**
  ```bash
  python scripts/docs_gate.py --fast
  ```
- **Validate Documentation (Full Gate - checks links):**
  ```bash
  python scripts/docs_gate.py --full
  ```

## Development Workflow
When performing tasks (implementing, investigating, auditing), follow the task-class routing defined in `docs/INDEX.md` and `docs/development/AGENT_WORKFLOW.md`. Always prioritize documentation according to the authority hierarchy specified in `docs/REFERENCE.md`.

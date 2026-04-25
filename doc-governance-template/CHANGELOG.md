---
doc_id: CHANGELOG
doc_class: historical
authority_kind: null
title: Template Changelog
primary_audience: all
task_entry_for: []
updated_by: human
status: active
depends_on: []
---

# Changelog

All notable changes to the Agentic OS Governance Template will be documented in this file.

## [1.2.0] - 2026-04-25

### Added
- **Multi-Agent Claim Protocol**: `scripts/claim_task.py` and `docs/history/AGENT_CLAIMS.md` for concurrency management.
- **Machine-Readable Evidence Standard**: Structured YAML blocks for `runtime_evidence` docs.
- **Advanced Drift Adapters**: `RequirementsPinAdapter`, `EnvVarAdapter`, and `GitHubActionsAdapter`.
- **Session Persistence**: `SESSION_ENVELOPE.md` and `scripts/manage_session.py` for cross-session continuity.
- **Shell Fail-Fast Enforcement**: `scripts/check_shell_scripts.py` and pre-commit hook for `set -euo pipefail`.
- **Structured Logging**: `scripts/governance_logger.py` and `docs/history/AGENT_AUDIT_TRAIL.jsonl`.
- **Formal Versioning**: Template versioning established in `.agent_config.yaml`.

### Changed
- **Decentralized Registry**: Migrated from a monolithic `DOC_REGISTRY.yaml` to distributed Markdown frontmatter aggregated by `aggregate_registry.py`.
- **Robust State Management**: `AGENT_STATE.md` refactored to use YAML frontmatter; `manage_agent_state.py` refactored for robust object manipulation.
- **CI Enhancements**: `agent-os-gate.yml` updated to use `aggregate_registry.py`.

### Fixed
- **Health Score Bug**: `calculate_health_score.py` refactored to read from `.registry_cache.json`.
- **Phantom Script References**: Removed all references to non-existent `build_doc_registry_md.py`.
- **Syntax Issues**: Fixed various script errors in `check_needs_attention.py` and legacy test blockers.

## [1.1.0] - 2026-04-24

### Added
- **Initial Governance Core**: `docs_gate.py`, `detect_drift.py` (Docker), and `propose_fixes.py`.
- **Registry Aggregator**: `aggregate_registry.py`.
- **Agent Workflow**: Formal task routing and closure rules.

# Documentation Governance Template

A portable documentation governance framework for AI-assisted development. Drop this into any repo to establish an authority hierarchy, task-routing rules, and automated quality gates that prevent documentation drift.

## What This Provides

- **Authority hierarchy** — explicit priority order so agents and humans know which doc wins when two docs conflict
- **Task-class routing** — INDEX.md routes by task type (implement / investigate / audit), not by topic
- **Staleness as metadata** — `last_verified` and `verification_level` in a registry, not freeform timestamps
- **Closure output contract** — every implementation task ends with a structured summary
- **Known conflicts registry** — explicit entries for where docs disagree + resolution chain
- **Automated quality gate** — `scripts/docs_gate.py` validates registry integrity, metadata, and link health

## Quick Start

1. Copy this directory's **contents** (not the directory itself) into your repo root
2. Merge `CLAUDE.md` into your existing `CLAUDE.md`, or use it as-is if you don't have one
3. Customize the three placeholder-heavy files:
   - `docs/INDEX.md` — update task routes to point to your project's actual docs
   - `docs/REFERENCE.md` — fill in your project's authority surface map
   - `docs/development/AGENT_WORKFLOW.md` — update task class details for your stack
4. Add entries to `docs/reference/registry/DOC_REGISTRY.yaml` for every governed doc in your project
5. Install dependency: `pip install pyyaml`
6. Generate the registry markdown: `python scripts/build_doc_registry_md.py`
7. Run the gate: `python scripts/docs_gate.py --fast` — all checks should pass

## Directory Structure After Copying

```
your-repo/
├── CLAUDE.md                                   # Agent behavioral guardrails
├── docs/
│   ├── INDEX.md                                # Universal navigation entrypoint
│   ├── REFERENCE.md                            # "Where is the truth?" authority surface map
│   ├── development/
│   │   ├── AGENT_WORKFLOW.md                   # Normative task routing for agents
│   │   ├── DOCUMENTATION_MAINTENANCE.md        # Maintenance procedures
│   │   └── RELEASE_CHECKLIST.md                # Pre-release doc checks
│   └── reference/
│       └── registry/
│           ├── DOC_REGISTRY.yaml               # Canonical doc registry (source of truth)
│           └── DOC_REGISTRY.md                 # Human-readable view (generated)
└── scripts/
    ├── build_doc_registry_md.py                # Generate DOC_REGISTRY.md from YAML
    ├── check_doc_registry.py                   # Validate registry structure
    ├── check_doc_metadata.py                   # Validate per-entry metadata
    ├── check_doc_registry_sync.py              # Verify MD matches YAML
    ├── validate_doc_links.py                   # Check internal markdown links
    └── docs_gate.py                            # Orchestrate all checks
```

## Core Concepts

### Authority Kinds (priority order, high to low)

| authority_kind | Answers |
|---|---|
| `runtime_evidence` | What has been verified in the live environment |
| `current_config` | What source artifacts currently define |
| `blueprint` | How this is designed / intended implementation |
| `plan` | Why we're doing this and in what order |
| `guide` | How to execute or operate safely |

When two docs conflict on a mutable fact, prefer the one with higher authority_kind. If same kind, prefer the one with a more recent `last_verified` in the registry.

### Doc Classes

| doc_class | Meaning |
|---|---|
| `entrypoint` | Navigation only — no factual claims |
| `active` | Human-maintained, normative |
| `generated` | Auto-refreshed from source artifacts |
| `historical` | Archived, superseded |

### Task Classes

The framework ships with 6 task classes. Customize them for your project in `AGENT_WORKFLOW.md` and `INDEX.md`:

| Task class | Meaning |
|---|---|
| `implement_change` | Source code or config changes |
| `investigate_runtime_issue` | Diagnosing bugs or service failures |
| `refresh_current_docs` | Updating docs after source artifacts change |
| `update_plan_or_roadmap` | Updating planning or roadmap docs |
| `operate_or_release` | Deploying or releasing |
| `test_or_operate_dev_environment` | Working in a non-production environment |

## Scripts

All scripts run from the repo root. Requires Python 3.8+ and `pyyaml`:

```bash
pip install pyyaml

# Regenerate DOC_REGISTRY.md from DOC_REGISTRY.yaml (run after any registry edit)
python scripts/build_doc_registry_md.py

# Fast gate — required before every commit touching docs/ or governed source artifacts
python scripts/docs_gate.py --fast

# Full gate — run before significant releases (adds broken link check)
python scripts/docs_gate.py --full

# Run individual checks
python scripts/check_doc_registry.py        # Registry structure and schema
python scripts/check_doc_metadata.py        # Per-entry required metadata
python scripts/check_doc_registry_sync.py   # MD matches YAML
python scripts/validate_doc_links.py        # Internal markdown links
```

## Customization Checklist

- [ ] Replace all `[YOUR-PROJECT-NAME]` and `[YOUR-PROJECT-DESCRIPTION]` placeholders
- [ ] Replace all `[YOUR-NAME]` placeholders in `DOC_REGISTRY.yaml`
- [ ] Update task-class routes in `docs/INDEX.md` to point to your actual docs
- [ ] Fill in the authority surface map in `docs/REFERENCE.md`
- [ ] Update task class details in `docs/development/AGENT_WORKFLOW.md` with your stack's specific sources and paths
- [ ] Add entries to `docs/reference/registry/DOC_REGISTRY.yaml` for all your governed docs
- [ ] Run `python scripts/build_doc_registry_md.py` to generate `DOC_REGISTRY.md`
- [ ] Run `python scripts/docs_gate.py --fast` — all checks should pass before first commit
- [ ] Merge `CLAUDE.md` documentation governance section into your project's `CLAUDE.md`

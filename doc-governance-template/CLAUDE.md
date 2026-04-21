# CLAUDE.md

<!-- This file provides guidance to Claude Code and other AI agents.
     Merge the "Documentation Governance" section below into your existing CLAUDE.md,
     or use this file as a starting point and add your project-specific sections. -->

## Documentation Navigation

This file contains agent behavioral guardrails and operational rules. For current system state:
- **Task routing**: [`docs/INDEX.md`](docs/INDEX.md)
- **Authority surface map**: [`docs/REFERENCE.md`](docs/REFERENCE.md)
- **Agent task routing**: [`docs/development/AGENT_WORKFLOW.md`](docs/development/AGENT_WORKFLOW.md)
- **Documentation registry**: [`docs/reference/registry/DOC_REGISTRY.yaml`](docs/reference/registry/DOC_REGISTRY.yaml)

<!-- Add project-specific navigation links here. Examples:
- **Service placement and ports**: `docs/reference/current/SERVICE_INVENTORY.md`
- **Runtime health**: `docs/reference/current/SYSTEM_RUNTIME_STATUS.md`
- **Workflow catalog**: `docs/reference/current/WORKFLOW_CATALOG.md`
-->

---

## Agent-First Documentation Operating Rules (Mandatory)

### 1) Deterministic entrypoint
Always start with:
1. `docs/INDEX.md`
2. `docs/development/AGENT_WORKFLOW.md`
3. `docs/reference/registry/DOC_REGISTRY.yaml`

Do not draw conclusions from `CLAUDE.md` alone. It is an entrypoint and quick reference, not a runtime authority.

### 2) Authority hierarchy (strict)
- `runtime_evidence` — live system verification (SSH output, monitoring, deploy evidence)
- `current_config` — source artifacts (YAML, compose files, schema files, config files)
- `blueprint` — intended design docs (architecture, API contracts, interface specs)
- `plan` — roadmap, decisions, sequencing documents
- `guide` — CLAUDE.md, operational guides (behavioral rules only, not mutable facts)
- `entrypoint` — INDEX.md, README (routing only, no factual claims)

When docs conflict on a mutable fact: source + runtime evidence wins always. CLAUDE.md is authoritative for behavioral rules only.

### 3) Host/environment truth rules (do not infer)
<!-- Fill in your project's canonical host/environment facts. Examples:
- Production: `10.0.0.20` (until a documented decision + verified evidence changes this)
- Staging: `10.0.1.20` — separate environment, not production
- Prod/dev distinction must always be written explicitly in documentation
-->

### 4) Evidence standard before doc changes
Every claim in a `current_config` or `runtime_evidence` doc must have:
- host/IP or source file reference
- exact command or reference used to derive the claim
- timestamp
- key output (brief)
- conclusion + confidence (`verified` / `partial` / `unverified`)

Do not write "confirmed" without evidence.

### 5) Required doc update matrix
When runtime/config changes, update at minimum:
- Relevant `current_config` doc (e.g., service inventory)
- Relevant `runtime_evidence` doc if service state changed
- `docs/reference/registry/DOC_REGISTRY.yaml` if a new governed doc is created
- Run `python scripts/build_doc_registry_md.py` after any registry change

<!-- Add project-specific update requirements here -->

### 6) Registry + gate are mandatory
After every documentation change:
1. `python scripts/build_doc_registry_md.py`
2. `python scripts/check_doc_registry_sync.py`
3. `python scripts/docs_gate.py --fast`

Work is not complete without a passing gate result.

### 7) Drift prevention contract
- "Task done" is not valid if docs/registry metadata is stale (`last_verified`, `verification_level`, notes).
- If something could not be verified, record it as `unverified` + next action.
- Do not close a task with empty `unresolved_drift` if host-level or container-level checks are missing from the requested scope.

### 8) Decision control
Do not assume a migration (e.g., host move, service rename) without:
1. A recorded decision (commit/doc/ADR) AND
2. Runtime evidence + publish evidence.

If either is missing, record "no authoritative decision found" and keep documentation in the current verified state.

### 9) Generated-doc policy
Do not hand-edit generated outputs.
Update the master/source and run the generator.
Document what is source vs generated in DOC_REGISTRY.yaml (`updated_by: agent` and `source_inputs` fields).

### 10) Required closure output format
End every implementation or operation task with this structure:

```
### Task Closure Summary
- **changed_sources**: [source files modified — YAML, JSON, TypeScript, SQL, etc.]
- **updated_blueprints**: [blueprint docs updated — or "none"]
- **updated_current_docs**: [current_config docs refreshed — or "none"]
- **updated_runtime_evidence**: [runtime_evidence docs updated — or "none"]
- **unresolved_drift**: [discrepancies left open — missing docs, conflicts, stale claims]
- **roadmap_impact**: [phase affected — or "none"]
- **follow_up_required**: [next tasks, missing docs to create]
```

This contract is mandatory for all runs that modify sources or documentation.

---

<!-- ============================================================
     PROJECT-SPECIFIC SECTIONS BELOW
     Add your project's architecture overview, critical development
     rules, key URLs, service map, SSH access patterns, etc.
     ============================================================ -->

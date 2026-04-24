---
doc_id: DOCUMENTATION_MAINTENANCE
doc_class: active
authority_kind: guide
title: "Documentation Maintenance \u2014 Procedures and Expectations"
primary_audience: both
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- documentation maintenance procedures
- docs gate invocation and interpretation
- when to update which docs (refresh trigger table)
- closure output format
- how to add a new governed doc
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
# Documentation Maintenance

**doc_id**: DOCUMENTATION_MAINTENANCE
**doc_class**: active
**authority_kind**: guide
**edit_policy**: human

---

## Purpose

This document defines how documentation is maintained in this repo. It is the authoritative source for documentation maintenance procedures and expectations.

---

## Documentation Model

Every doc in this repo carries two axes of classification. The `doc_class` axis describes lifecycle state: `entrypoint` (navigation only), `active` (human-maintained, normative), `generated` (auto-refreshed from source artifacts), or `historical` (archived). The `authority_kind` axis describes what kind of question the doc can answer with authority: `plan` (why and in what order), `blueprint` (how it is designed), `guide` (how to execute), `current_config` (what source artifacts currently define), or `runtime_evidence` (what has been verified in the live environment).

These axes determine where to write facts and where to read them. For example: a new service port belongs in the relevant config source file and is reflected in a `current_config` doc — it does not belong as an inline claim in a `guide`-class doc like CLAUDE.md. The full classification of every registered doc is in [DOC_REGISTRY.yaml](../reference/registry/DOC_REGISTRY.yaml).

---

## When Documentation Must Be Updated

| Change type | Required doc updates | When |
|---|---|---|
| New doc created in `docs/` | Add metadata header to doc; add entry to `docs/reference/registry/DOC_REGISTRY.yaml`; run `python scripts/docs_gate.py --fast` | Before commit |
| Markdown frontmatter edited on any governed doc | Run `python scripts/aggregate_registry.py`; commit updated `.registry_cache.json` and `DOC_REGISTRY.md` | Before commit |
| Source artifact changed (schema, config, etc.) | Update relevant `current_config` doc | Before commit |
| Runtime behavior verified (SSH or monitoring) | Update relevant `runtime_evidence` doc with evidence entry; update `last_verified` in registry | After verification |
| Service migrated to different host | Update service placement doc; update runtime status doc's pending list | Before commit |

<!-- Add project-specific rows here. Examples:
| `infra/docker-compose.yml` changed | Update `SERVICE_INVENTORY.md` (service name, port, host) | Before commit |
| DB schema YAML changed | Run `python scripts/generate_all.py` + `integrity_check.py`; update schema current_config doc | Before commit |
| Workflow JSON added/modified | Run workflow catalog generator; commit updated catalog | Before commit |
-->

---

## Closure Output Requirements

Every implementation task must produce a structured closure summary. This is the required format (from [AGENT_WORKFLOW.md Section 5](AGENT_WORKFLOW.md)):

```
### Task Closure Summary
- **changed_sources**: [source files modified — YAML, JSON, TypeScript, SQL, etc.]
- **updated_blueprints**: [blueprint docs updated to reflect the change — or "none"]
- **updated_current_docs**: [current_config docs refreshed — or "none"]
- **updated_runtime_evidence**: [runtime_evidence docs updated if runtime behavior changed — or "none"]
- **unresolved_drift**: [discrepancies left open — missing docs, unresolved conflicts, stale claims encountered]
- **roadmap_impact**: [does this change affect phase planning? If yes, which phase?]
- **follow_up_required**: [next tasks needed — including any missing docs that should be created]
```

For audit and review tasks (`refresh_current_docs`, `investigate_runtime_issue`), include:
- `evidence_produced` instead of `changed_sources`
- `docs_updated` for any docs modified
- `conflicts_resolved` for any known conflicts now resolved
- `conflicts_remaining` for any conflicts still open

### When is closure mandatory vs optional?

- **Mandatory** for: `implement_change`, `operate_or_release`
- **Optional** (but encouraged) for: `refresh_current_docs`, `investigate_runtime_issue`
- **Not applicable**: `update_plan_or_roadmap` — plan docs use their own format

---

## Fake Closure Indicators

The following patterns constitute non-compliant closure. Treat any of these as a signal that the task is incomplete.

1. **"Done" claimed with no closure summary produced.** A response that ends with a description of changes but omits the structured `### Task Closure Summary` block is non-compliant for `implement_change` and `operate_or_release` tasks.

2. **`changed_sources` lists only `docs/` files when source artifacts were actually modified.** If a schema, config file, or source artifact was edited, those must appear in `changed_sources`. Listing only the doc that was updated to reflect the change is incomplete.

3. **`updated_current_docs` is "none" when a tracked source artifact was changed.** Every `implement_change` that modifies a tracked source artifact requires a corresponding current_config doc update. "none" is only valid if no tracked source artifact was changed.

4. **`unresolved_drift` is left blank when a known conflict was encountered.** If the agent encountered a stale claim, a conflicting doc, or a missing doc during the task, that must be recorded — even if the task itself succeeded.

5. **`roadmap_impact` is "none" when a phase deliverable was completed.** If the task delivered a phase item, the relevant phase and item must be named.

---

## Running the Docs Gate

```bash
# Fast mode (registry + metadata + registry-sync checks) — required before every commit touching docs/
python scripts/docs_gate.py --fast

# Full mode (adds link validation) — run before significant releases
python scripts/docs_gate.py --full
```

Gate output: `[PASS]`, `[WARN]`, or `[FAIL]` per check. Exit code 1 on any `[FAIL]`.

- **`--fast`**: required before commit for any change touching `docs/` or governed source artifacts
- **`--full`**: run before merging governance changes or significant releases (adds link validation)

---

## Refresh Triggers

| Source file | Refresh trigger | Which doc to update |
|---|---|---|
| Any `docs/**/*.md` frontmatter | `on_source_change` | `.registry_cache.json` + `DOC_REGISTRY.md` (run `python scripts/aggregate_registry.py`) |

<!-- Add your project-specific rows here. Examples:
| `docker-compose.yml` | `on_source_change` | `docs/reference/current/SERVICE_INVENTORY.md` |
| `infra/n8n/workflows/*.json` | `on_source_change` | `docs/reference/current/WORKFLOW_CATALOG.md` |
| `schema.yaml` | `on_source_change` | `docs/reference/current/DATABASE_SCHEMA.md` |
-->

---

## Adding a New Governed Doc

1. Add the file under the correct path in `docs/`
2. Add a metadata header block at the top of the doc:
   ```
   **doc_id**: YOUR_DOC_ID
   **doc_class**: active
   **authority_kind**: guide
   **edit_policy**: human
   ```
3. Add an entry to `docs/reference/registry/DOC_REGISTRY.yaml` with all required fields
4. Run `python scripts/aggregate_registry.py` to rebuild the registry cache and regenerate the registry view
5. Run `python scripts/docs_gate.py --fast` to verify
6. Include the gate result in your task closure summary

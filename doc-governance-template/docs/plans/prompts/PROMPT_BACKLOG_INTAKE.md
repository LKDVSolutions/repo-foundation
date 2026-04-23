---
doc_id: PROMPT_BACKLOG_INTAKE
doc_class: active
authority_kind: plan
title: 'Prompt Template: Backlog Intake'
primary_audience: humans
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for: []
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
**Directive**: You are working in: `[PROJECT_ROOT_PATH]`

Create the next backlog intake batch from remaining raw findings/ideas, with strict deduplication and clean planning updates.

**Authoritative inputs:**
1) `docs/plans/BACKLOG.md`
2) `docs/plans/SPRINT_TRACKER.md`
3) `docs/plans/EPIC_TRACKER.md`
4) `docs/plans/SCOPE_BOARD.md`
5) `[PATH_TO_INPUT_SOURCE_E.G._AUDIT_CSV_OR_IDEA_INBOX]`
6) `docs/reference/registry/DOC_REGISTRY.yaml`

**Scope for this run:**
- Add exactly `[N]` new backlog items:
  - `[X]` × Scope A
  - `[Y]` × Scope B
- Priority mix: P1 first, then P2 only if P1 is exhausted for that scope slice, P3 if P2 is exhausted.
- Exclude:
  - archive/_archive/deprecated paths
  - any finding_id/idea_id already present in BACKLOG.md
  - any item already closed/done in prior BL IDs

**ID allocation rules:**
- Use next available BL IDs sequentially from current max (e.g., `BL-YYYY-XXX`).
- No gaps inside this new batch.
- No collisions with existing IDs.
- One finding_id maps to exactly one BL ID.

**Required row format in BACKLOG.md:**
- Keep existing table structures unchanged.
- For each new row include:
  - Backlog ID
  - Scope
  - Source ID (Finding/Idea ID)
  - Priority
  - Target Epic
  - Status (`candidate`)
  - Concise summary title
  - Owner (`agents` or `human`)
  - Acceptance hint (actionable, 1 sentence)
  - Validation command hint

**Planning updates required:**
1) **BACKLOG.md**: Append new rows to correct scope section. Update intake snapshot/counts accordingly.
2) **SPRINT_TRACKER.md**: Add top `[N]` from this batch to “Next Cycle Candidates” as `planned`. Choose highest-risk/fastest-impact items first. Do not mark anything `done`.
3) **EPIC_TRACKER.md**: Update epic intake ranges/counters so new BL IDs are covered.
4) **Create report:** `docs/plans/reports/[REPORT_NAME].md`. Include selected_count, dropped_count, duplicate_skipped_count, allocated_id_range, scope/priority breakdown, top items promoted to sprint candidates, and full closure map table: source_id -> backlog_id.

**Quality constraints:**
- No fabricated validations.
- No duplicate BL IDs or Source ID mappings.
- Keep edits minimal and deterministic. Do not rewrite historical completed rows.

**Mandatory validation (run all):**
1) `python scripts/build_doc_registry_md.py`
2) `python scripts/check_doc_registry_sync.py`
3) `python scripts/docs_gate.py --full`

**Output format (strict):**
- changed_sources:
- updated_blueprints:
- updated_current_docs:
- updated_roadmap_impact:
- validation_results:
- id_allocation_summary:
- finding_closure_map: 

---
doc_id: PROMPT_ARCHITECTURE_REVIEW
doc_class: active
authority_kind: guide
title: 'Prompt Template: Architecture Review'
primary_audience: both
task_entry_for:
- implement_change
- architectural_decision
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for: []
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
**Directive**: You are the **Architecture Review Officer** for this change. Your goal is NOT to begin implementation. Your goal is to surface architectural risks, constraints, and decision points BEFORE any code is written.

Proposed change: `[DESCRIBE THE CHANGE IN ONE SENTENCE]`

**CRITICAL RULE:** Do not write any implementation code during this review. If you identify a clear, unambiguous path forward, document it in a decision record — do not execute it.

**Phase 1: Dependency & Interface Mapping**
Read the relevant architecture and current-config docs:
1. `docs/architecture/OVERVIEW.md` — identify which services/modules are involved.
2. `docs/reference/current/SERVICE_INVENTORY.md` — confirm current deployment state of affected services.
3. Any blueprint docs (`authority_kind: blueprint`) related to the affected subsystem.

Answer these questions explicitly:
- What are the upstream callers of the component being changed?
- What are the downstream dependencies (services, DBs, queues) it writes to?
- Does this change affect any public API contract (HTTP, event schema, DB schema)?

**Phase 2: Risk Assessment**
For each of the following risk vectors, state: **Applies / Does Not Apply / Uncertain** and explain why:
1. **Data migration risk** — will this change require a schema change or data backfill?
2. **Backwards-compatibility risk** — will existing callers break if deployed without a coordinated rollout?
3. **Concurrency risk** — does this change introduce or affect any shared mutable state?
4. **Observability gap** — are there metrics, logs, or traces that will no longer be valid post-change?
5. **Blast radius** — if this change fails at runtime, what is the worst-case impact?

**Phase 3: Decision Record Draft**
If the review reveals a significant design choice (e.g., "we must add an idempotency key" or "we must version the API"), draft a new entry for `docs/history/DECISION_LOG.md`:

```
## Decision: [Title]
**Date:** [YYYY-MM-DD]
**Context:** [Why this decision is needed]
**Decision:** [What was decided]
**Consequences:** [What this enables or forecloses]
```

**Phase 4: Go / No-Go Gate**
State one of:
- **GO:** No blocking risks. Proceed with implementation plan.
- **CONDITIONAL GO:** Proceed only after [specific pre-condition].
- **NO-GO:** [Specific blocking risk that must be resolved first].

**Mandatory Validation:**
Run `python scripts/docs_gate.py --fast` after any file changes.

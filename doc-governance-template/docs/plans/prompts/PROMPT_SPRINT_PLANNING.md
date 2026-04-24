---
doc_id: PROMPT_SPRINT_PLANNING
doc_class: active
authority_kind: guide
title: 'Prompt Template: Sprint Planning'
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

Your mission is to produce a structured sprint plan for the upcoming sprint by reading the current governance artifacts and proposing a realistic, prioritized work package.

**CRITICAL RULE:** Do NOT assume sprint state from memory. Read the current files directly.

**Phase 1: Current-State Ingestion**
Read the following files in order and extract their current state:
1. `docs/plans/[SPRINT_TRACKER.md]` — identify the most recently completed sprint number and its velocity (points completed vs committed).
2. `docs/plans/[EPIC_TRACKER.md]` — identify all in-progress and next-up epics with their priorities.
3. `docs/plans/[SCOPE_BOARD.md]` — identify all items in `Ready` status and their estimated effort.

**Phase 2: Capacity Calculation**
1. Calculate available capacity: `[TEAM_SIZE] × [SPRINT_DAYS] × [HOURS_PER_DAY] = total_hours`. Convert to points using the project's velocity ratio from Phase 1.
2. Identify carry-over items from the previous sprint (incomplete items with dependencies).
3. Subtract carry-over from available capacity to get net new capacity.

**Phase 3: Scope Proposal**
Select items from the `Ready` column of SCOPE_BOARD.md in priority order until net new capacity is consumed. Respect these rules:
- **No scope creep:** Do not pull items not in `Ready` status.
- **Epic alignment:** Prefer items that advance an in-progress epic over starting a new one.
- **Risk buffer:** Reserve 15% of capacity as an unplanned work buffer.

**Phase 4: Sprint Plan Output**
Produce the following structured output:

```
## Sprint [N+1] Plan

**Capacity:** [X] points
**Carry-over:** [list items]
**Committed Scope:**
| Item ID | Title | Epic | Points | Owner |
|---------|-------|------|--------|-------|
| ...     | ...   | ...  | ...    | ...   |

**Risk Buffer:** [Y] points reserved

**Success Criteria:**
- [ ] [Item 1 done condition]
- [ ] [Item 2 done condition]
```

**Mandatory Validation:**
Run `python scripts/docs_gate.py --fast` to ensure your actions did not break the documentation registry.

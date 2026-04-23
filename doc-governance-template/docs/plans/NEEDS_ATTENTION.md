---
doc_id: NEEDS_ATTENTION
doc_class: active
authority_kind: plan
title: Human-Agent Handoff (Interrupts)
primary_audience: both
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- agent blockers and handoff status
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
# Human-Agent Handoff (Interrupts)

When an agent hits an unresolvable blocker (e.g., missing dependencies, ambiguous architectural choice, repeated errors, missing credentials), it should stop attempting to fix the issue blindly and document the block here.

## Active Blocker

**Date:** [YYYY-MM-DD]
**Agent Session / Task:** [Task ID or Description]

### 1. The Blocker
[Describe exactly what is blocking progress]

### 2. Current State
[Describe what has been accomplished so far and the state of the codebase]

### 3. Proposed Options
[Provide 2-3 options for how the human operator can unblock this issue]
- **Option A:** [Description]
- **Option B:** [Description]
- **Option C:** [Description]

### 4. Next Steps
[What the agent will do once unblocked]

**Directive**: Round 2 QA Gate (mandatory). 

You are reviewing your own just-completed batch for regression/drift before handoff. Do not skip checks. If anything fails, fix it immediately and rerun all checks.

**Inputs:**
- Batch backlog IDs: `[COMMA_SEPARATED_LIST_OF_BL_IDS]`
- Allowed files: `[PASTE_FILE_LIST_FROM_BATCH_PROMPT]`

**Steps:**

1. **Verify scope discipline:**
  - Confirm every edited file is in the allowed files list.
  - Confirm each backlog ID has at least one concrete change mapped to its suggested action.
  - Confirm no generated artifacts were hand-edited.

2. **Diff quality review:**
  - Check for accidental behavior changes outside acceptance scope.
  - Check for hardcoded absolute paths, host IPs, env-specific values, and brittle string matching.
  - Check idempotency/replay safety for write paths (atomic writes, no silent destructive overwrite).

3. **Run validation commands (must all pass):**
  - `[PASTE_EXACT_BATCH_VALIDATION_COMMANDS]`
  - `python scripts/docs_gate.py --full`

4. **Apply fixes:** For any failed check, apply the fix, then rerun the full validation set.

**Output format:**
- qa_verdict: PASS | FAIL
- backlog_ids_verified: [...]
- file_scope_check: PASS | FAIL
- validation_results:
  - <command>: PASS/FAIL + short evidence
- fixes_applied_in_qa: <none or list>
- residual_issues: <none or list>
- ready_for_final_commit: yes/no

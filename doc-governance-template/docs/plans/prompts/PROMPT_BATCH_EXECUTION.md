**Directive**: You are working in: `[PROJECT_ROOT_PATH]`

Target: Continue backlog execution. Start with the first `[N]` `planned` items in the range `[BL-YYYY-XXX..YYY]` from `docs/plans/BACKLOG.md`.

**Close backlog IDs:** `[COMMA_SEPARATED_LIST_OF_BL_IDS]`

**Files you may edit ONLY (Strict Boundary):**
- `[FILE_PATH_1]`
- `[FILE_PATH_2]`
- `[FILE_PATH_3]`

**Rules:**
- Implement minimal, deterministic fixes per the suggested action in the backlog.
- Implement fixes directly in source files (not generated artifacts).
- Do NOT hardcode absolute paths, host IPs, env-specific values, or use brittle string matching.
- Keep generated output authority boundaries intact.
- Update `docs/plans/BACKLOG.md` status and summary for each completed item:
  - `done` for implemented fix.
  - `verified-no-change` only with explicit concrete evidence in the summary.
- Keep all other backlog IDs unchanged. Do not rewrite historical completed rows.

**Validation (mandatory):**
- Run syntax checks for touched files (e.g., `python -m py_compile ...` or `bash -n ...`).
- Run specific tests: `[SPECIFIC_VALIDATION_COMMAND]`
- Run full gate: `python scripts/docs_gate.py --full`
- If any check fails, fix and re-run until PASS.

**Output format (strict):**
- backlog_ids_done: [...]
- changed_files: [...]
- validation_commands_and_results:
  - <cmd>: PASS/FAIL
- residual_risks: [...]
- ready_for_qa_gate: yes/no

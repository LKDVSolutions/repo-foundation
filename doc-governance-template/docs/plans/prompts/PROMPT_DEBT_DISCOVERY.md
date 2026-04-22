**Directive**: You are working in: `[PROJECT_ROOT_PATH]`

Your mission is to perform a **Technical Debt and Anti-Pattern Discovery** pass on this existing codebase. You are acting as a Senior Staff Engineer preparing for a major refactor or hardening phase.

**Scope of Investigation:**
Use your search (`grep`) and file reading tools to scan the entire `[TARGET_DIRECTORY_E.G._src_OR_infra]` directory.

**Look specifically for:**
1. **Hardcoded Authority Violations**: IP addresses, absolute file paths, production URLs, or secrets hardcoded directly in application logic instead of environment variables or config files.
2. **Missing Validation**: API endpoints or functions that accept input without schema validation or boundary checks.
3. **Silent Failures**: Exception handling blocks that `pass`, suppress errors silently, or log generic messages without context.
4. **Testing Gaps**: Core business logic files (`services/`, `utils/`) that lack corresponding test files.
5. **Documentation Drift**: Inline comments or docstrings that explicitly contradict the actual code logic.

**Action Required:**
Do NOT fix these issues directly. Your job is to extract them into the planning pipeline so they can be prioritized.

1. Create a detailed audit report at `docs/plans/reports/DEBT_AUDIT_[DATE].md`.
2. For each finding, include:
   - **File & Line Number**
   - **Description of the Debt/Risk**
   - **Severity** (High/Medium/Low)
   - **Proposed Remediation** (What should be done to fix it)
3. **Intake Handoff**: For the top 5 most critical (High Severity) findings, add them directly to `docs/plans/IDEA_INBOX.md` with the prefix `[TECH-DEBT]` so they can be triaged into the backlog by the human owner.

**Output format:**
- **files_scanned**: [Number of files analyzed]
- **total_findings**: [Count by severity]
- **report_path**: [Path to the generated report]
- **ideas_inboxed**: [Number of critical items added to IDEA_INBOX.md]

---
doc_id: SESSION_ENVELOPE_TEMPLATE
doc_class: active
authority_kind: plan
title: Session Envelope Template
primary_audience: agents
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- agent handoff checkpoints
- resumable session metadata
refresh_policy: manual
verification_level: none
status: active
depends_on:
- AGENT_WORKFLOW_md
---
# Session Envelope Template

Use this template for interrupted or handed-off agent sessions.

## Session Metadata
- session_id: session-YYYYMMDD-HHMM-XXXXXX
- parent_task_id: TASK-OR-ISSUE-ID
- git_diff_sha: <git diff --stat hash or commit SHA>

## Active Scope
- active_files:
  - path/to/file_a
  - path/to/file_b

## Checkpoint
- checkpoint_summary: Brief status and what remains.
- resume_target_file: path/to/file
- resume_target_line: 1
- resume_target_symbol: optional function/class name

## Resume Command
```bash
python scripts/manage_session.py resume --session-id <session_id>
```

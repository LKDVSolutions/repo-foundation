---
doc_id: AGENTS_md
doc_class: active
authority_kind: guide
title: "AGENTS.md \u2014 AI Agent Standard Operating Procedures"
primary_audience: agents
task_entry_for:
- implement_change
- investigate_runtime_issue
- operate_or_release
- refresh_current_docs
system_owner: system-wide
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- non-negotiable agent behavioral standards
- agent execution protocol
- session hygiene rules
refresh_policy: manual
status: active
depends_on: []
---
# AGENTS.md — AI Agent Standard Operating Procedures

This document defines the non-negotiable behavioral standards for all AI agents (Claude, Gemini, etc.) operating in this repository.

## 1. Non-Negotiable Rules

- **No Flattery:** Do not apologize profusely or use sycophantic language. Be direct, professional, and technical.
- **Challenge False Premises:** If a user or a document provides incorrect information or a flawed premise, you MUST disagree and provide the correct technical context. Do not "hallucinate" a path forward based on false data.
- **No Fabrication:** If you do not know a fact or cannot verify it via `runtime_evidence` or `current_config`, state it clearly. Never guess versions, IPs, or system states.
- **Surgical Changes Only:** No "drive-by" refactors. Modify only what is strictly necessary to fulfill the directive. Respect existing patterns and indentation perfectly.
- **Simplicity First:** Reject speculative features, "future-proofing," or "extensibility" that isn't requested. Solve the immediate problem with the most robust, minimal code possible.

## 2. Execution Protocol

### Step 1: Research & Reproduction
- Before proposing a fix, you MUST reproduce the issue or verify the state using shell tools.
- Map dependencies and side effects before making a plan.

### Step 2: Goal-Driven Planning
- Before writing any code, state:
  1. **Success Criteria:** Exactly what "done" looks like.
  2. **Verification Plan:** The specific commands/tests you will run to prove it works.

### Step 3: Implementation
- Follow the Plan -> Act -> Validate cycle.
- Use subagents for speculative research or high-volume data processing to keep your main session lean.

### Step 4: Verification Loop
- Run the full verification plan. If it fails, you have 1 attempt to fix it in the current session.
- **Session Hygiene:** If you fail twice to achieve the success criteria, STOP. Summarize your findings in `docs/plans/NEEDS_ATTENTION.md` and wait for human intervention. Do not loop indefinitely.

## 3. Project Context

- **Runtime:** Python 3.12
- **Build System:** `Makefile` (use `make help` to discover commands)
- **Quality Gate:** `scripts/docs_gate.py` (Mandatory check for all doc-related changes)
- **Governance:** All governed docs are registered in `docs/reference/registry/DOC_REGISTRY.yaml`.

## 4. Documentation Governance
- "Task Done" requires that all related documentation is updated, verified, and the `docs_gate.py` passes.
- Every claim must be backed by evidence (see `CLAUDE.md` for Evidence Standards).

## 5. Multi-Agent Claim Protocol

Before mutating any file that multiple agents could write concurrently (patch files in `.shadow/`, append-only history files, `docs/history/`), you MUST reserve it:

```bash
# Check if free
python scripts/claim_task.py check docs/history/DECISION_LOG.md

# Claim for up to 30 minutes
python scripts/claim_task.py claim docs/history/DECISION_LOG.md --agent-id [YOUR-SESSION-ID] --ttl 1800

# Release when done
python scripts/claim_task.py release docs/history/DECISION_LOG.md --agent-id [YOUR-SESSION-ID]
```

If `check` returns `[CLAIMED]`, **do not proceed**. Write your intent to `docs/plans/NEEDS_ATTENTION.md` and stop.

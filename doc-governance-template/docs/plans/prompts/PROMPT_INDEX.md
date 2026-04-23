---
doc_id: PROMPT_INDEX
doc_class: active
authority_kind: guide
title: Prompt Library Index
primary_audience: both
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- standardized agent prompt templates
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
# Prompt Library Index

**doc_id**: PROMPT_INDEX
**doc_class**: active
**authority_kind**: guide
**primary_audience**: both
**edit_policy**: human

---

## Purpose

This library contains standardized System Prompts (Instructions) for AI Agents. Instead of writing custom prompts for every operation, humans use these templates to ensure agents operate within the repository's strict governance and planning frameworks.

To use these, copy the raw markdown of a prompt, replace the `[BRACKETED_PLACEHOLDERS]` with your specific context, and pass it to your LLM (via CLI or Web interface).

## Available Prompts

| Workflow | Prompt File | Use Case |
|---|---|---|
| **System Audit** | [PROMPT_SYSTEM_AUDIT.md](PROMPT_SYSTEM_AUDIT.md) | Deep architectural discovery and mapping for existing codebases (Retrofits) |
| **Debt Discovery** | [PROMPT_DEBT_DISCOVERY.md](PROMPT_DEBT_DISCOVERY.md) | Deep scan for hardcoding, anti-patterns, and unverified assumptions |
| **Dependency Bootstrap** | [PROMPT_DEPENDENCY_BOOTSTRAP.md](PROMPT_DEPENDENCY_BOOTSTRAP.md) | Forces agents to verify exact package versions online and strictly pin them |
| **Backlog Intake** | [PROMPT_BACKLOG_INTAKE.md](PROMPT_BACKLOG_INTAKE.md) | Moving raw ideas/audits into the prioritized Backlog |
| **Batch Execution** | [PROMPT_BATCH_EXECUTION.md](PROMPT_BATCH_EXECUTION.md) | Assigning a surgical fix batch to an agent (Strict scope) |
| **QA Gate Review** | [PROMPT_QA_GATE.md](PROMPT_QA_GATE.md) | Forcing an agent to review its own batch before finalizing |

---

## The "Agent API" Contract

When using these prompts, agents are expected to:
1. Only read the explicitly listed authoritative inputs.
2. Only modify the explicitly allowed files (strict surgical edits).
3. Produce the exact output schema requested (for human/script parsing).
4. Run all mandatory validation commands and fix failures autonomously before reporting completion.

# Planning Index

**doc_id**: PLANNING_INDEX
**doc_class**: active
**authority_kind**: plan
**primary_audience**: both
**edit_policy**: human

---

## Purpose

Deterministic planning entrypoint for this repository. It defines the strict lifecycle of how an idea becomes executed code, preventing agents (and humans) from jumping straight into coding without defining the problem.

---

## The "0 to 1" Lifecycle

Before any code is written or tools are configured, work must pass through these stages:

### Phase 1: Intake & Discovery
1. **Raw Intake:** Drop rough concepts into [IDEA_INBOX.md](IDEA_INBOX.md).
2. **Problem Definition:** If an idea is accepted, write a `PROBLEM_STATEMENT` using [docs/plans/templates/PROBLEM_STATEMENT.md](templates/PROBLEM_STATEMENT.md). **No technology discussion allowed here.**

### Phase 2: System Design
3. **Architecture Decision:** Once the problem is approved, evaluate technical solutions using an `ARCHITECTURE_DECISION` record [docs/plans/templates/ARCHITECTURE_DECISION.md](templates/ARCHITECTURE_DECISION.md).

### Phase 3: Execution Planning
4. **Backlog & Epics:** Break the chosen architecture into actionable units. (e.g., Epics, Sprints, Tasks).
5. **Execution:** Agents and humans execute the work using the rules in `AGENT_WORKFLOW.md`.

---

## Rules for Agents

1. **Never skip Phase 1 or 2.** If a user asks you to "build X", you must first check if a Problem Statement and ADR exist. If not, inform the user and offer to draft the Problem Statement.
2. **No direct execution from Idea Inbox.**
3. **Technology belongs in Phase 2.** If drafting a Problem Statement, strictly enforce the rule to avoid discussing languages, frameworks, or architecture.

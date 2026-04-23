---
doc_id: CONTRIBUTING_md
doc_class: entrypoint
title: "Contributing Guide \u2014 Rules of the House"
primary_audience: both
task_entry_for:
- bootstrap_project
status: active
depends_on: []
authoritative_for: []
system_owner: system-wide
doc_owner: '[YOUR-NAME]'
updated_by: human
refresh_policy: manual
---
# Contributing to [YOUR-PROJECT-NAME]

This guide defines the "Rules of the House" for [YOUR-PROJECT-NAME]. It ensures that both humans and AI agents follow the same physics for documentation, development, and strategic decision-making.

---

## ⚖️ The Non-Negotiable "Truth Rule"
**A fact only exists if recorded in a documented Truth Surface.**
- **`runtime_evidence`** (live verification) > **`current_config`** (source files) > **`blueprint`** (design).
- **If it's not verified, it's not "Done."** Plausibility is not correctness. All agents and humans must provide shell-verified output for every claim.

## 🤖 The AI-Human Contract
Our AI agents are not "Yes-Men." They are senior architects programmed with **Strategic Friction**:
1.  **Expected Pushback**: If your initial proposal is technically unsound, the agent will (and must) challenge your premise.
2.  **Socratic Skepticism**: Agents will ask "Why?" and "What is the alternative?" at least twice before proposing a plan.
3.  **No flattery, no filler**: Agents skip the pleasantries and start with technical rationale or action.
4.  **Verification Loop**: Agents must prove their work with a script or test before declaring a task finished.

---

## 🏛️ Planning Hierarchy
We maintain strict context isolation for AI agents via this hierarchy:

1.  **Strategic (Day 0)**: Challenges vision, researches dependencies, and identifies core risks.
    - Start at: [`docs/plans/prompts/PROMPT_STRATEGIC_ALIGNMENT.md`](docs/plans/prompts/PROMPT_STRATEGIC_ALIGNMENT.md)
2.  **Tactical (Epics & Sprints)**: Sets goals, organizes work packages, and maps the architecture.
    - Start at: [`docs/architecture/OVERVIEW.md`](docs/architecture/OVERVIEW.md)
3.  **Operational (Tasks)**: Individual implementation, bug fixes, or operations.
    - Start at: [`docs/INDEX.md`](docs/INDEX.md) and [`CLAUDE.md`](CLAUDE.md) / [`GEMINI.md`](GEMINI.md)

---

## 🛠️ The Pre-Code Checklist
Before writing a single line of code, verify these **5 mandatory items**:

1.  **[Project-Specific Rule 1]**: (e.g., "All [Resource X] must have [Attribute Y]") — *Fill this in for your project.*
2.  **Authority Check**: Have you identified the `current_config` or `runtime_evidence` that owns this class of fact in [`docs/REFERENCE.md`](docs/REFERENCE.md)?
3.  **Success Criteria**: Have you explicitly stated exactly what "done" looks like with a verification command?
4.  **Surgical Changes**: Does this change touch only what is strictly necessary? (No drive-by refactors).
5.  **Documentation Sync**: Will this change require an update to the Documentation Registry (`DOC_REGISTRY.yaml`)?

---

## 🔄 Development Workflow

1.  **Discovery**: Audit the current state via the registry or `PROMPT_SYSTEM_AUDIT.md`.
2.  **Planning**: Use the appropriate prompt from `docs/plans/prompts/`.
3.  **Implementation**: Follow the [**Agent Workflow**](docs/development/AGENT_WORKFLOW.md).
4.  **Verification**: Run the [**Quality Gate**](docs/development/ENGINEERING_STANDARDS.md):
    ```bash
    python scripts/docs_gate.py --fast
    ```

---

## 📚 Quick Navigation
- **Task Routing**: [`docs/INDEX.md`](docs/INDEX.md)
- **Technical Standards**: [`docs/development/ENGINEERING_STANDARDS.md`](docs/development/ENGINEERING_STANDARDS.md)
- **Operational Commands**: [`docs/development/USER_MANUAL.md`](docs/development/USER_MANUAL.md)
- **Agent behavioral rules**: [`AGENTS.md`](AGENTS.md)

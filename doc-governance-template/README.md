# Agentic OS Governance Template

A portable, "0-to-1" Agentic Operating System and documentation governance framework. Drop this into any repository to establish strict authority hierarchies, task-routing rules, automated quality gates, and deterministic agent prompts that prevent AI hallucinations and documentation drift.

## What This Provides

- **The Bootstrapper** — `scripts/init_project.py` initializes the workspace and generates explicit instructions for your LLM (CLI or Web) to wake up and take control safely.
- **Planning Lifecycle (0-to-1)** — Strict progression from `IDEA_INBOX` → `PROBLEM_STATEMENT` → `ARCHITECTURE_DECISION` → `BACKLOG` to stop agents from writing code before defining the problem.
- **The Prompt Library** — Pre-compiled, deterministic system prompts (`docs/plans/prompts/`) for Backlog Intake, Batch Execution, System Audits, and QA Self-Review.
- **Authority Hierarchy** — Explicit priority order (`runtime_evidence` > `current_config` > `blueprint`) so agents and humans know which doc wins when two docs conflict.
- **Security & Engineering Guardrails** — Baked-in enforcement of the OWASP Top 10, Microsoft SDL, strict dependency pinning, and idempotency rules.
- **Automated Quality Gate** — `scripts/docs_gate.py` validates registry integrity, metadata staleness, and link health before commits.

---

## 🚀 How to Use This System (User Manual)

### Step 1: Initialization (The Handoff)

Do not manually copy-paste placeholders. Run the bootstrapper:

```bash
python scripts/init_project.py
```

1. **Answer the prompts:** The script will ask for your Project Name and whether this is a **[1] Blank Canvas** (new project) or a **[2] Retrofit** (existing codebase).
2. **Wake up the Agent:** The script will generate a `.gemini/boot_instruction.md` file. It will print a command for you to run (e.g., `gemini "Read .gemini/boot_instruction.md..."`) or tell you to copy-paste the contents into ChatGPT/Claude.
3. **Follow the Agent's Lead:** 
   - *If Blank Canvas:* The agent will enter Product Manager mode and interview you to draft a `PROBLEM_STATEMENT.md`.
   - *If Retrofit:* The agent will enter Systems Architect mode, scan your codebase, map your architecture, and populate the documentation registry.

### Step 2: Planning & Discovery

Never let an agent write code without a plan. Use the [Prompt Library](docs/plans/prompts/PROMPT_INDEX.md) to guide your AI:

- **Have a new idea?** Drop it in `docs/plans/IDEA_INBOX.md`.
- **Retrofitting an old codebase?** Give the agent `PROMPT_SYSTEM_AUDIT.md` to map the architecture, and then `PROMPT_DEBT_DISCOVERY.md` to find technical debt and hardcoded secrets.
- **Ready to prioritize?** Give the agent `PROMPT_BACKLOG_INTAKE.md` to move ideas into the prioritized `BACKLOG.md`.

### Step 3: Execution (Surgical Agent Work)

When you are ready to write code or fix bugs, do not give the agent an open-ended prompt. 

1. Copy the `PROMPT_BATCH_EXECUTION.md` template.
2. Fill in the specific Backlog IDs and strictly define the **Allowed Files** the agent is permitted to touch.
3. Pass the prompt to your agent. The agent is forced to stick to those boundaries and run validation commands.

### Step 4: QA and Validation

Before merging or calling a task "Done", force the agent to review its own work:

1. Pass the agent the `PROMPT_QA_GATE.md` template.
2. The agent will verify it did not break scope, check for hardcoded values, and run the automated `docs_gate.py` script.
3. If the gate fails, the agent must fix it autonomously.

---

## Directory Structure

```text
your-repo/
├── CLAUDE.md                                   # Agent behavioral guardrails
├── .github/workflows/agent-os-gate.yml         # CI/CD enforcement
├── .gitignore                                  # Includes `.agent_context.md` & scratchpad
├── docs/
│   ├── INDEX.md                                # Universal navigation entrypoint
│   ├── REFERENCE.md                            # Authority surface map ("Where is the truth?")
│   ├── architecture/                           # High-level system design
│   ├── development/                            # Engineering standards, security rules, workflow
│   │   └── AGENT_CAPABILITIES.md               # What the agent is permitted/able to do
│   ├── plans/
│   │   ├── IDEA_INBOX.md                       # Raw intake for ideas/findings
│   │   ├── NEEDS_ATTENTION.md                  # Human-Agent Handoff (Interrupts)
│   │   ├── PLANNING_INDEX.md                   # 0-to-1 lifecycle rules
│   │   ├── prompts/                            # Standardized AI Agent prompt templates
│   │   └── templates/                          # PRD and ADR templates
│   └── reference/
│       └── registry/
│           ├── DOC_REGISTRY.yaml               # Canonical doc registry (source of truth)
│           └── DOC_REGISTRY.md                 # Human-readable view (generated)
└── scripts/
    ├── hydrate_context.py                      # Compiles agent "RAM" context
    ├── detect_drift.py                         # Auto-drift detection cron script
    ├── init_project.py                         # Agentic OS Bootstrapper
    ├── build_doc_registry_md.py                # Generates DOC_REGISTRY.md from YAML
    ├── docs_gate.py                            # Orchestrates all registry/metadata checks
    └── ...                                     # Validation sub-scripts
```

## Security & Engineering Mandates

This template enforces strict guardrails found in `docs/development/`.
- **`SECURITY_AND_DEPENDENCIES.md`**: Enforces strict dependency pinning (no LLM version guessing), the OWASP Top 10 (2025), and Microsoft SDL practices.
- **`ENGINEERING_STANDARDS.md`**: Enforces idempotency in scripts, Infrastructure as Code, "Fail Fast" blast radiuses, and structured observability.

## Manual Maintenance (Scripts)

If you modify the documentation registry manually, you must run the gate:

```bash
# Regenerate DOC_REGISTRY.md from DOC_REGISTRY.yaml
python scripts/build_doc_registry_md.py

# Fast gate — required before every commit touching docs/
python scripts/docs_gate.py --fast

# Full gate — run before significant releases (adds broken link check)
python scripts/docs_gate.py --full
```

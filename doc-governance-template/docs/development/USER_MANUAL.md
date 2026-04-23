# User Manual: Operating with the Documentation Governance Template

This guide explains how to use this template to build new software, refactor legacy code, or manage existing systems with high-autonomy AI agents.

## 1. Starting a New Project (Day 0)

If you are starting with an empty repository and a new idea:

1.  **Initialize the Environment**:
    ```bash
    make build  # Sets up basic dependencies
    ```
2.  **Run the Strategic Challenge**:
    Point your agent to `docs/plans/prompts/PROMPT_STRATEGIC_ALIGNMENT.md`.
    *   **The Goal**: The agent will act as a skeptical CTO, researching dependencies, checking licenses, and challenging your scope before any code is written.
    *   **The Output**: A "Go/No-Go" report and an initial `docs/architecture/DECISION_LOG.md`.

## 2. Refactoring or Migrating Legacy Code

If you have a "massive monolith" and want to perform a structural refactor:

1.  **Map the Current Truth**:
    Run `python scripts/discover_unregistered_docs.py` and `python scripts/generate_tree.py` to see what you have.
2.  **Audit the System**:
    Use `docs/plans/prompts/PROMPT_SYSTEM_AUDIT.md`.
    *   **The Action**: The agent will read your source code to create an authoritative `docs/reference/current/SERVICE_INVENTORY.md` and `docs/REFERENCE.md`.
    *   **The Result**: You now have a "Truth Map" that tells the agent which files are the `current_config` (the source of truth).
3.  **Execute the Refactor**:
    Use the `implement_change` task routing in `docs/INDEX.md`. The agent will use the newly created truth map to ensure the refactor matches the actual code, not just your memory of it.

## 3. Adding Features to Existing Microservices

When adding a feature to a complex, multi-service environment:

1.  **Hydrate Context**:
    Run `python scripts/hydrate_context.py --github --jira` (if configured).
    *   **Why**: This pulls live PR diffs and ticket requirements into the agent's memory so it understands the *intent* behind the change.
2.  **Follow the Gate**:
    Every change must end with:
    ```bash
    python scripts/docs_gate.py --fast
    ```
    If the agent misses a metadata field or breaks a link between services, the gate will fail.

## 4. Recovering from "Manual Drift"

If someone (human or a legacy script) has altered files outside of this process:

1.  **Detect the Drift**:
    ```bash
    python scripts/detect_drift.py
    ```
    This script compares your `current_config` (e.g., `docker-compose.yml` or source code) against your `blueprint` docs.
2.  **Auto-Fix the Registry**:
    If new files were added manually without registration:
    ```bash
    python scripts/auto_fix_registry.py
    ```
3.  **Self-Heal the Docs**:
    If documentation headers or sections are missing:
    ```bash
    python scripts/auto_fix.py
    ```

## 5. Human-Agent Collaboration (The Interrupt)

This framework is highly autonomous, but it is designed to stop when it hits high-risk ambiguity.

*   **When the Agent Stops**: If an agent fails a verification loop twice, it will log its state to `docs/plans/NEEDS_ATTENTION.md` and "ring the bell" using `scripts/request_human.py`.
*   **Your Action**: Check `NEEDS_ATTENTION.md`. It will contain a JSON-lite payload of the agent's memory and the exact blocker. Fix the blocker, update the doc, and tell the agent to "Resume from NEEDS_ATTENTION."

## 6. Key Commands Reference

| Command | Purpose |
|---|---|
| `make gate` | Run the mandatory documentation quality check. |
| `make build` | Install dependencies and prepare the environment. |
| `python scripts/calculate_health_score.py` | Get a % score of how "governed" your repo is. |
| `python scripts/cascade_staleness.py` | Automatically mark docs as stale when their code dependencies change. |

---

**Remember**: In this repo, **Verified Truth > Plausible Fiction**. If the `docs_gate.py` fails, the task is not done.

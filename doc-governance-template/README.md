# Agentic OS Governance Template

A "0-to-1" framework for establishing strict documentation authority, task-routing, and deterministic agent workflows. Use this to turn any repository into a self-governing "Agent OS" that prevents AI hallucinations and technical drift.

## 🚀 30-Second Start

1.  **Initialize the Environment**:
    ```bash
    make build
    python scripts/init_project.py
    ```
2.  **Wake up the Agent**: 
    Follow the generated instructions in `.gemini/boot_instruction.md` to hand over control to your AI (Claude, Gemini, or ChatGPT).
3.  **Run the Strategic Challenge**:
    Point your agent to [`docs/plans/prompts/PROMPT_STRATEGIC_ALIGNMENT.md`](docs/plans/prompts/PROMPT_STRATEGIC_ALIGNMENT.md).

---

## 🗺️ Navigation Map

*   **New to the repo?** Read [**`CONTRIBUTING.md`**](CONTRIBUTING.md) first. It defines the "Rules of the House" and how you and the AI work together.
*   **Need deep-dive commands?** See the [**User Manual**](docs/development/USER_MANUAL.md).
*   **Looking for specific docs?** Check the [**Repository Index**](docs/INDEX.md) or the [**Documentation Registry**](docs/reference/registry/DOC_REGISTRY.md).

## ⚖️ The Core Mandate
**Truth Over Plausibility.** In this repository, if a fact is not recorded in a documented Truth Surface (`current_config` or `runtime_evidence`), it does not exist. All changes must be verified against the live environment before they are considered "Done."

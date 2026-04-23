# Engineering Philosophy — The Human Manual

This document explains the "why" behind the strict governance and operational standards in this repository. It is intended for both human engineers and AI agents to understand the core values of our development process.

## 1. Truth Over Plausibility

In the age of LLMs, it is easy to generate "plausible" but incorrect code, documentation, or system configurations. Our philosophy rejects plausibility in favor of **Verified Truth**.

- **Governance is Mandatory:** We do not trust memory (human or agent). We trust current configuration and runtime evidence.
- **Evidence as Currency:** A claim without a command, a timestamp, and an output is considered unverified.
- **Authority Hierarchy:** We use a strict hierarchy (`runtime` > `config` > `blueprint`) to resolve conflicts. This ensures that the documentation reflects reality, not just intent.

## 2. Agent Autonomy & Strategic Friction

We design our system to enable agents to work autonomously, but we introduce **Strategic Friction** where necessary to prevent catastrophic failure.

- **Phase of Strategic Friction:** When a project is in a high-risk or foundational state, we enforce strict planning modes, mandatory gate checks, and limited attempt loops. This "friction" is a feature, not a bug; it forces the agent (and the human) to slow down and verify assumptions.
- **Agent as Peer:** We treat the agent as a senior engineer, not a "tool." We expect them to challenge false premises, refuse flattery, and maintain their own session hygiene.

## 3. Simplicity & Surgicality

Technical debt often starts with "future-proofing."

- **No Speculative Engineering:** We build exactly what is needed for the current requirement. No "maybe we'll need this" features.
- **Surgical Changes:** We prefer small, precise modifications over sweeping refactors. This keeps the codebase stable and the diffs readable.
- **Explicit Rationale:** Every change must have a clear "why." This rationale is as important as the "what."

## 4. Documentation as Code

Documentation is not an after-thought; it is a primary artifact of the engineering process.

- **The Registry is Sacred:** Every governed document must be registered and its metadata (last verified, verification level) must be kept current.
- **Automated Gates:** If the documentation is drift-prone or inaccurate, the "build" is broken. We use `docs_gate.py` to enforce this.

## 5. Summary

We value:
- **Accuracy** over speed.
- **Verification** over assumption.
- **Simplicity** over complexity.
- **Autonomy** through rigorous guardrails.

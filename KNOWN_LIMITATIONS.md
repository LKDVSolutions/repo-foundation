# Known Limitations

This file is the publishable summary of the current gaps, partial implementations, and practical constraints in this repository.

It is derived from the internal `DEVELOPMENT.md` working notes, but is intentionally more stable and external-facing.

Use this file to understand what works well today, what is only partially implemented, and where adopters should expect manual work or tighter operational discipline.

## Best Fit Today

This repository currently works best for teams that:

- are comfortable with strict documentation and governance workflows
- want strong consistency and explicit process over minimal setup
- use GitHub as their primary source-control and CI platform, or are willing to adapt the workflow to another platform
- are primarily working in a Python-centric environment around this template

This repository is likely a poor fit if you want a lightweight, low-process starter repo with minimal documentation overhead.

## Current Limitations

### 1. Jira integration is only a stub
- Current state: Jira support exists only as a placeholder in the context hydration path.
- Impact: real Jira-backed context hydration or backlog syncing is not available.

### 2. Branch-policy verification is only automated for GitHub
- Current state: GitHub branch protection can be verified automatically, but other providers do not yet have implemented adapters.
- Impact: non-GitHub teams must verify equivalent branch policy manually for now.

### 3. Dependency advisory scanning is Python-focused
- Current state: dependency advisory scanning currently covers the Python manifest used by this template.
- Impact: this is not yet a generalized multi-ecosystem supply-chain verification framework.

### 4. Multi-agent concurrency is intentionally limited
- Current state: the file-lock coordination model is intentionally operated at roughly 10 concurrent agents or fewer.
- Impact: higher parallelism is expected to create contention and operational friction.

### 5. Direct one-command self-healing is not supported
- Current state: the old direct auto-fix path is deprecated. The supported model is proposal-first and review-driven.
- Impact: repairs may still be suggested automatically, but a human review step is expected before changes are applied.

### 6. CI portability is still manual outside the GitHub reference implementation
- Current state: the repository includes GitHub Actions as the working reference implementation for the quality gates.
- Impact: teams using Azure DevOps or another CI system must translate that setup themselves.

### 7. The governance model is intentionally heavy
- Current state: the template expects governed frontmatter, registry generation, and gate-driven documentation discipline.
- Impact: the setup and maintenance overhead is higher than in a typical lightweight repository template.

## Practical Guidance

- If you want the most complete experience today, use GitHub and keep the default governance flow intact.
- If you adopt this template on another platform, plan for some manual translation work around CI and branch policy.
- If your team is small or wants a lighter process, start by evaluating whether the governance overhead is acceptable before adopting the full template.

## Contributions Welcome

Several of the limitations listed here are good candidates for future improvement.

- If a missing feature matters for your usage, open an issue or start a discussion.
- If you already have a working improvement, a focused pull request is welcome.
- Provider-specific adapters, CI translations, and improvements to currently stubbed areas are especially useful when they are driven by real usage.

## Internal vs External Notes

- `KNOWN_LIMITATIONS.md`: publishable, curated summary for adopters and testers
- `DEVELOPMENT.md`: private working notes for ongoing development, partial ideas, and local memory
# Development Notes

This is a working development-status document for the repository.

It is not a strict backlog and it is not a polished roadmap. The purpose is to keep track of:

- features that are planned but not implemented yet
- features that exist only as stubs or placeholders
- known limitations that testers should be aware of
- provider-specific gaps where one platform works and others do not yet

This file is intentionally kept out of version control so it can be practical, candid, and useful for day-to-day development and tester communication.

## How To Use This File

- Add items when something is intentionally deferred, stubbed, or only partially implemented.
- Update items when the situation changes enough that testers or future development work would be affected.
- Remove items when the limitation or stub is fully resolved.
- Keep entries short and concrete. Focus on what is missing, what works today, and what the impact is.

## Item Format

Use this structure when adding new entries:

### DEV-XXX: Short title
- Status: planned | stubbed | partial | known limitation
- Area: feature area or subsystem
- Current state: what exists today
- Impact: what a developer or tester should expect
- Next step: the most likely next move when this comes back into focus

---

## Current Items

### DEV-001: Jira integration is only a stub
- Status: stubbed
- Area: external context hydration
- Current state: `hydrate_context.py` contains a Jira placeholder path, but not a real Jira REST integration.
- Impact: enterprise backlog syncing or real Jira-backed context hydration does not work yet.
- Next step: implement actual Jira API integration only if there is real demand for it.

### DEV-002: Branch-policy verification is only automated for GitHub
- Status: partial
- Area: repository security / SCM integration
- Current state: GitHub branch protection is implemented and can be verified automatically. Other providers such as Azure DevOps are not yet wired to an adapter.
- Impact: the security outcome is still expected, but non-GitHub platforms currently require manual verification.
- Next step: add provider-specific adapters only when there is a clear need.

### DEV-003: Dependency advisory scanning is Python-focused
- Status: known limitation
- Area: supply-chain verification
- Current state: dependency advisory scanning is implemented for the Python manifest used by the template.
- Impact: this improves security for the current template, but it is not yet a generalized multi-ecosystem advisory framework.
- Next step: expand only if the template starts managing additional package ecosystems in practice.

### DEV-004: Concurrency is intentionally capped by the file-lock design
- Status: known limitation
- Area: multi-agent coordination
- Current state: the current design is intentionally operated at no more than about 10 concurrent agents per project.
- Impact: above that level, lock contention and timeout-related friction become likely.
- Next step: redesign coordination only if real usage proves that higher concurrency is needed.

### DEV-005: Direct self-healing is no longer supported
- Status: known limitation
- Area: documentation repair workflow
- Current state: the old `auto_fix.py` path is deprecated. The supported path is proposal-based and writes suggested patches for review instead of directly repairing files in place.
- Impact: users expecting one-command automatic self-repair will not get that behavior. A human review step is still required.
- Next step: keep the proposal-first model unless there is a strong reason to reintroduce a safer privileged apply path.

### DEV-006: CI portability is still manual outside the reference implementation
- Status: partial
- Area: CI/CD integration
- Current state: the template ships with GitHub Actions as the working reference implementation for the quality gates.
- Impact: teams using Azure DevOps or another CI system must translate the gate, drift, and advisory jobs themselves.
- Next step: add provider-specific CI examples only if multiple adopters need them.

### DEV-007: Governance setup is intentionally strict and can feel heavy for small repos
- Status: known limitation
- Area: onboarding and day-to-day maintenance
- Current state: the template expects governed frontmatter, registry generation, and gate-driven documentation discipline.
- Impact: this improves consistency, but it also raises the setup and maintenance overhead compared with a lightweight repo.
- Next step: do not relax the core rules by default; instead, document lighter-weight usage patterns if smaller teams keep hitting the same friction.

## Not For This File

Do not use this file for:

- completed implementation history
- detailed design decisions that belong in architecture docs
- sensitive internal notes that should stay private to local scratch files
- large task breakdowns that belong in a real backlog or execution plan

## Working Rule

If a tester could reasonably ask "does this actually work yet?" or "what should I expect here?", the answer probably belongs in this file.

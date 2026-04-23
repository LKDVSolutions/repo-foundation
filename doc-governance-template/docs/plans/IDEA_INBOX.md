# Idea Inbox

**doc_id**: IDEA_INBOX
**doc_class**: active
**authority_kind**: plan
**primary_audience**: both
**edit_policy**: human

---

## Purpose

The single intake surface for all new ideas, problems, and requests before they are formally defined. 

This file is intentionally lightweight:
1. Capture the raw idea or problem.
2. If it's worth pursuing, create a `PROBLEM_STATEMENT.md`.
3. Do **not** execute work directly from this file.

**Promotion Path:**
`IDEA_INBOX` -> `PROBLEM_STATEMENT` -> `ARCHITECTURE_DECISION` -> `BACKLOG`

---

## Intake Rules

1. Every new idea gets a unique `IDEA-YYYY-NNN` id.
2. Ideas should be brief. Focus on the "What" and "Why", not the "How".
3. Curation involves either rejecting the idea or promoting it to the Problem Definition phase.

---

## Open Ideas

| Idea ID | Date | Title / Raw Problem | Source | Status | Next Action |
|---|---|---|---|---|---|
| IDEA-2026-001 | YYYY-MM-DD | [Example: Need a way to easily bootstrap new projects from the template] | Human | new | Draft Problem Statement |

---

## Rejected / Parked

| Idea ID | Date | Reason | Decision Owner |
|---|---|---|---|
| | | | |

## Automated Drift Report
**Detected:** docker-compose: 2 service(s) in source not in blueprint: ['db', 'web']

## Automated Drift Report
**Detected:** docker-compose: 1 service(s) in blueprint not in source: ['worker']

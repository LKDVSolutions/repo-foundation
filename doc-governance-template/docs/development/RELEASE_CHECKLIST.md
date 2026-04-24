---
doc_id: RELEASE_CHECKLIST
doc_class: active
authority_kind: guide
title: "Release Checklist \u2014 Pre-Release Documentation Checks"
primary_audience: agents
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- pre-release documentation check sequence
- per-change check requirements
- advisory (non-blocking) checks
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
# Release Checklist

**doc_id**: RELEASE_CHECKLIST
**doc_class**: active
**authority_kind**: guide
**edit_policy**: human

---

## Pre-Release Documentation Checks

Run before any deploy or merge to main:

### Fast Gate (required)
- [ ] `python scripts/docs_gate.py --fast` — exits 0

### Per-Change Checks

**If `docs/` was modified:**
- [ ] All new docs have metadata headers (`doc_id`, `doc_class`, `authority_kind`, `edit_policy`)
- [ ] Markdown frontmatter updated on any new or modified docs
- [ ] `python scripts/aggregate_registry.py` ran — `.registry_cache.json` and `DOC_REGISTRY.md` are committed

**If source artifacts changed (schema, config, etc.):**
- [ ] Relevant `current_config` doc updated
- [ ] If generated files exist, generators were run and generated files committed

**If services added or moved:**
- [ ] Service placement doc updated
- [ ] `DOC_REGISTRY.yaml` updated if new docs were created

<!-- Add project-specific checks here. Examples:

**If DB schema changed:**
- [ ] `python scripts/generate_all.py` ran successfully
- [ ] `python scripts/integrity_check.py` passed

**If workflows changed:**
- [ ] Workflow catalog generator ran
- [ ] Updated catalog committed
-->

### Closure Summary
- [ ] Task closure summary produced (see [DOCUMENTATION_MAINTENANCE.md](DOCUMENTATION_MAINTENANCE.md))
- [ ] `unresolved_drift` recorded if any conflicts remain open
- [ ] `roadmap_impact` evaluated

---

## Advisory Checks (non-blocking)

- Runtime evidence docs older than 7 days: flag for verification
- Blueprint docs with no `last_verified`: schedule verification
- Docs with `verification_level: none` carrying runtime claims: review for removal or migration to evidence-backed surface

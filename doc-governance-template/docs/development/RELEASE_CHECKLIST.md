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
- [ ] `python scripts/check_dependency_advisories.py` — exits 0

### Branch Policy Verification (provider-specific)
- [ ] Default branch protection or policy requires checks equivalent to `doc-gate`, `drift-detection`, and `dependency-advisory`
- [ ] If using GitHub, `python scripts/verify_branch_protection.py` exits 0
- [ ] If using another provider, manual verification is recorded until a provider adapter exists

### Per-Change Checks

**If template governance files changed (scripts, templates, config schema):**
- [ ] `.agent_config.yaml` `template.version` updated when behavior or schema changed
- [ ] `docs/reference/TEMPLATE_CHANGELOG.md` updated with migration notes
- [ ] `template.last_migrated` and `template.changelog_ref` remain valid

**If dependency manifests or CI workflows changed:**
- [ ] `requirements-dev.txt` remains strictly pinned
- [ ] `dependency-advisory` remains present in `.github/workflows/agent-os-gate.yml`
- [ ] The platform-native default branch policy still requires checks equivalent to `doc-gate`, `drift-detection`, and `dependency-advisory`

**If `docs/` was modified:**
- [ ] All new docs have metadata headers (`doc_id`, `doc_class`, `authority_kind`, `edit_policy`)
- [ ] Markdown frontmatter updated on any new or modified docs
- [ ] `python scripts/aggregate_registry.py` ran — `.registry_cache.json` and `DOC_REGISTRY.md` are committed

**If source artifacts changed (schema, config, etc.):**
- [ ] Relevant `current_config` doc updated
- [ ] If generated files exist, generators were run and generated files committed

**If services added or moved:**
- [ ] Service placement doc updated
- [ ] Frontmatter added or updated and `python scripts/aggregate_registry.py` run if new governed docs were created

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
- Extra required GitHub checks beyond the documented baseline: review docs for drift, even if enforcement is stronger than required
- Non-GitHub branch policy verification performed manually: confirm the manual record remains current until an adapter exists

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
- [ ] `DOC_REGISTRY.yaml` updated with entries for any new docs
- [ ] `python scripts/build_doc_registry_md.py` ran — `DOC_REGISTRY.md` is committed

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

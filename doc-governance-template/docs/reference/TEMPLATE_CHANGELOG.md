---
doc_id: TEMPLATE_CHANGELOG
doc_class: active
authority_kind: guide
title: Template Changelog
primary_audience: both
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- template version history
- template migration notes
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
# Template Changelog

Tracks governance-template version changes and migration impact.

## 1.1.0 - 2026-04-24

### Added
- `.agent_config.yaml` `template` section with `version`, `last_migrated`, and `changelog_ref`.
- `scripts/manage_agent_state.py` refactor to frontmatter-aware, lock-protected state updates.
- `tests/test_manage_agent_state.py` coverage for resilient state updates.

### Changed
- `docs/history/AGENT_STATE.md` now uses governed frontmatter metadata.
- Engineering and release policy now include template versioning requirements.

### Migration Notes
- Existing projects should add the `template` block to `.agent_config.yaml` if missing.
- No data migration is required for `AGENT_STATE.md`; frontmatter normalization is backward compatible.

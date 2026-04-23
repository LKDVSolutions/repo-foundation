---
doc_id: REFERENCE_md
doc_class: active
authority_kind: guide
title: "[YOUR-PROJECT-NAME] \u2014 Where Is the Truth?"
primary_audience: both
task_entry_for: []
system_owner: system-wide
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- authority surface map (which source owns each class of fact)
- resolution chains for known conflicts
refresh_policy: manual
verification_level: none
status: active
notes: 'Where-is-the-truth map. Update when new current_config or runtime_evidence
  surfaces are added, or when a known transitional state is resolved.

  '
depends_on: []
---
# [YOUR-PROJECT-NAME] — Where Is the Truth?

**doc_id**: REFERENCE_md
**doc_class**: active
**authority_kind**: guide
**edit_policy**: human

This document maps every class of fact in this repository to its authoritative source. Before consuming any claim from any doc, check here to confirm which surface owns that fact.

---

## Authority Model

Every document in this repo is classified by `authority_kind`. The kind determines what question the doc can answer with authority:

| authority_kind | Answers | Examples |
|---|---|---|
| `plan` | "Why are we doing this and in what order?" | ROADMAP.md, ADRs, governance plans |
| `blueprint` | "How is this supposed to be built?" | Architecture docs, API specs, design documents |
| `guide` | "How do I execute or operate this safely?" | CLAUDE.md, REFERENCE.md, AGENT_WORKFLOW.md |
| `current_config` | "What do the source artifacts currently define?" | docker-compose.yml, schema files, config YAMLs |
| `runtime_evidence` | "What has actually been verified in the environment?" | SSH-verified service health docs, verified state docs |
| `entrypoint` | Navigation only — not authoritative for any mutable fact | INDEX.md, README.md |

**Priority rule (conflicts):** `runtime_evidence` > `current_config` > `blueprint` > `plan` > `guide`. If two docs of different authority_kind conflict on a mutable fact, prefer the higher-specificity source.

Full classification of all registered docs: [docs/reference/registry/DOC_REGISTRY.yaml](reference/registry/DOC_REGISTRY.yaml)

---

## Authority Surface Map

For each class of fact, this table identifies the single authoritative source.

**Fill this in for your project.** Common fact classes to define:

| Fact class | Authoritative source | Format | Notes |
|---|---|---|---|
| Agent behavioral guardrails | `CLAUDE.md` | Markdown | Behavioral rules only — not mutable facts |
| Documentation classification and routing | `docs/reference/registry/DOC_REGISTRY.yaml` | YAML | |
| Registry validation schema | `docs/reference/registry/DOC_REGISTRY.schema.json` | JSON | |
| CI/CD quality gate rules | `.github/workflows/agent-os-gate.yml` | YAML | |
| Dependency pinning and constraints | `requirements-dev.txt` | Text | |
| Local environment configuration | `.env.example` | Text | Blueprint for local dev |
| System architecture | `docs/architecture/OVERVIEW.md` | Markdown | |
| Automation service inventory | `docs/reference/current/SERVICE_INVENTORY.md` | Markdown | |

<!--
Add rows for every class of fact that matters in your project. Examples:
- Internal port assignments → docker-compose.yml
- Host-exposed port assignments → docker-compose.yml ports: mapping
- Build artifact paths → build config files
- Feature flag config → config YAML or feature flag service
- Third-party API keys → secret manager (source, not values)
- Infrastructure as code → Terraform/Pulumi source files
-->

---

## Known Transitional State

<!-- Document known authority boundary violations here as you discover them.
     These are places where the wrong doc currently carries a fact it shouldn't own.
     Example format:

### [Doc name]

**What it carries that it should not:**
- [Type of mutable fact that belongs in a current_config or runtime_evidence doc]

**What it IS authoritative for:**
- [Behavioral rules, navigation, design intent, etc.]

**Treatment:** [How agents should handle claims in this doc until the violation is resolved]
-->

No known transitional violations recorded yet. Add entries here when authority boundary violations are discovered during development or audits.

---

## Resolution Chains

<!-- When two docs conflict on a fact, document the resolution chain here.
     Example format:

### [Descriptive conflict name]

**Conflict:** `[Doc A]` says [X]. `[Doc B]` says [Y].

**Resolution:** [Which to trust and why — context-dependent or one clear winner]

**Authoritative source:** [The single source to check]
-->

No conflicts documented yet. Add entries here when two docs are found to give conflicting answers on the same fact.

---

*For full document classification and routing, see [docs/reference/registry/DOC_REGISTRY.yaml](reference/registry/DOC_REGISTRY.yaml).*
*For normative agent task routing, see [docs/development/AGENT_WORKFLOW.md](development/AGENT_WORKFLOW.md).*

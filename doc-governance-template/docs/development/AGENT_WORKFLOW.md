# Agent Workflow — Task Routing and Read-Order Rules

**doc_id**: AGENT_WORKFLOW_md
**doc_class**: active
**authority_kind**: guide
**primary_audience**: agents
**edit_policy**: human

This is a **normative** document. It prescribes required agent behavior. Following these rules is not optional — they prevent the most common documentation drift failure modes.

---

## Section 1: Required Read Order by Authority Kind

Before consuming any document, identify its `authority_kind` from [DOC_REGISTRY.yaml](../reference/registry/DOC_REGISTRY.yaml). Then apply the following read-order rules.

### When to read each kind

| authority_kind | Read this to answer | Do NOT use it to answer |
|---|---|---|
| `plan` | "Why are we doing this? What is the intended sequencing?" | "Is this service currently running?" or "What is the current config value?" |
| `blueprint` | "How is this supposed to be built? What is the intended design?" | "Is this currently deployed with these parameters?" |
| `current_config` | "What do the source artifacts currently define?" | "Is this verified working in production?" |
| `runtime_evidence` | "What has been verified in the live environment, and when?" | Structural design intent |
| `guide` | "How do I execute or operate this task safely?" | Current runtime state |
| `entrypoint` | Navigation to the right doc | Any mutable fact |

### Conflict priority

When two docs give conflicting answers, prefer the source with higher authority_kind specificity:

```
runtime_evidence  >  current_config  >  blueprint  >  plan  >  guide
```

Exception: CLAUDE.md (classified `guide`) is authoritative for **behavioral rules** regardless of this priority order. For mutable facts (IPs, ports, service health), it is not authoritative — use the resolution chains in [docs/REFERENCE.md](../REFERENCE.md#resolution-chains).

---

## Section 2: Task Class Routes

### Task class: implement_change {#task-class-implement_change}

Making a source code or config change — features, schema edits, workflow updates, config edits.

| Field | Value |
|---|---|
| Start at | `CLAUDE.md` (guardrails), then your project's roadmap or spec |
| Required read order | guide → plan → blueprint → current_config |
| Key authority surfaces | `CLAUDE.md` (rules), source schema files, config files, docker-compose.yml if applicable |
| Typical output | Modified source files, updated `current_config` docs if schema/config changed |
| Fallback rule | If a blueprint doc is missing, search source directories for the relevant config or schema artifact directly |

<!-- Customize for your project. Add:
- Specific YAML source files to check before editing
- Generate/integrity scripts to run after edits
- Which current_config docs need updating for which change types

Example:
**Mandatory steps before modifying YAML source files:**
1. Read CLAUDE.md "Source of Truth Architecture" section.
2. After editing any schema YAML, run `python scripts/generate_all.py` then `python scripts/integrity_check.py`.
3. Do not edit generated files.
-->

**Closure output required:** See Section 5.

---

### Task class: investigate_runtime_issue {#task-class-investigate_runtime_issue}

Diagnosing a bug, service failure, or unexpected behavior.

| Field | Value |
|---|---|
| Start at | `docs/REFERENCE.md` (resolution chains), then `CLAUDE.md` (service map) |
| Required read order | guide (REFERENCE.md) → blueprint → guide (CLAUDE.md) → runtime_evidence (if exists) |
| Key authority surfaces | Source config files, API contracts, live state exports |
| Typical output | Diagnosed root cause, fix applied or issue recorded, runtime_evidence doc updated if new evidence produced |
| Fallback rule | If runtime_evidence docs are missing, gather evidence directly (SSH, logs, monitoring); do not treat CLAUDE.md runtime claims as verified |

**Critical:** When a service health claim matters, verify via the live environment. See Section 3 for known conflicts. Do not trust any doc's `✅ Operational` annotation without a backing evidence trail.

---

### Task class: refresh_current_docs {#task-class-refresh_current_docs}

Updating `current_config` or `runtime_evidence` docs after source artifacts change.

| Field | Value |
|---|---|
| Start at | `docs/reference/registry/DOC_REGISTRY.yaml` (identify which docs are affected), then `docs/REFERENCE.md` (authority surface map) |
| Required read order | current_config (registry) → guide (REFERENCE.md) → current_config (affected source artifacts) |
| Key authority surfaces | `docs/reference/registry/DOC_REGISTRY.yaml`, source artifact for the changed system |
| Typical output | Updated `current_config` or `runtime_evidence` doc, updated `last_verified` and `verification_level` in DOC_REGISTRY.yaml |
| Fallback rule | If no current_config doc exists for the changed system, create one under `docs/reference/current/` before updating DOC_REGISTRY.yaml |

---

### Task class: update_plan_or_roadmap {#task-class-update_plan_or_roadmap}

Updating roadmap phases or planning docs.

| Field | Value |
|---|---|
| Start at | Your project's roadmap doc for current phase state |
| Required read order | plan (roadmap) → plan (ADRs or governance docs if applicable) |
| Key authority surfaces | Your project's roadmap doc |
| Typical output | Updated plan doc with phase goals or completion status |
| Fallback rule | If a governance plan is missing, create it in `docs/plans/` with a date-stamped filename |

**Rule:** Roadmap items must record **decisions** (a service was provisioned, configured, or deployed). They must NOT record runtime state ("currently running", "container is up"). Runtime health belongs in a `runtime_evidence` surface.

---

### Task class: operate_or_release {#task-class-operate_or_release}

Deploying, releasing, or operating a service — SSH commands, Docker operations, database migrations.

| Field | Value |
|---|---|
| Start at | `CLAUDE.md` (operational guardrails) |
| Required read order | guide (CLAUDE.md) → current_config (source config files) → blueprint (relevant service doc) |
| Key authority surfaces | `CLAUDE.md` (operational rules), source config files |
| Typical output | Service deployed or updated, runtime_evidence doc updated if service state changed |
| Fallback rule | If a service doc is missing, read the relevant config file (docker-compose.yml, etc.) before proceeding |

<!-- Add project-specific operational rules here. Example:
**Mandatory SSH rule:** All commands to a given host MUST be batched into a single SSH heredoc session.
Do not issue one `ssh host "cmd"` per command — it exhausts MaxStartups on the server.
-->

---

### Task class: test_or_operate_dev_environment {#task-class-test_or_operate_dev_environment}

Deploying to, operating, or validating a non-production environment.

| Field | Value |
|---|---|
| Start at | Your dev environment guide, then service placement doc, then runtime status doc |
| Required read order | guide (dev README) → current_config (dev config files) → runtime_evidence (dev runtime status) |
| Key authority surfaces | Dev environment config files, dev environment guide |
| Typical output | Dev stack updated, smoke-test run, runtime evidence captured, or validation gap recorded |
| Fallback rule | If a historical plan/spec disagrees with the implemented dev stack config, prefer the config over the plan |

**Critical rules for non-production environments:**
1. Dev is not production. Never infer production readiness from a successful dev smoke test.
2. Service presence in dev does not imply full validation. Record missing coverage in the closure summary.
3. For service placement and ports in dev, trust dev config files over older design docs.

---

## Section 3: Known Authority Conflicts

<!-- Document known conflicts here as they are discovered. This section starts empty
     and grows as your project evolves. Add an entry any time two docs give conflicting
     answers on the same mutable fact and you've determined the resolution.

Format:

### Conflict: [Descriptive name] {#conflict-name}

**Docs that conflict:**
- `[doc A path]` line [N]: says [X]
- `[doc B path]`: says [Y]

**Which source to trust:** [Which source is correct and why]

**Resolution chain:**
1. [How to determine the correct value]
2. [Where to look]
3. [What to update once resolved]
-->

No conflicts currently documented. Add entries here when two docs are found to disagree on the same fact.

---

## Section 4: Fallback Rules

These rules apply when expected documents are missing or when two sources conflict with no resolution chain defined above.

1. **Missing required doc:** Log the missing doc_id in the task closure `unresolved_drift` field. Proceed by searching the relevant source directories for the artifact directly. Do not halt.

2. **Two docs conflict, no resolution chain defined:** Prefer the source with higher authority_kind (see Section 1). If same kind, prefer the one with a more recent `last_verified` in DOC_REGISTRY.yaml. If neither has one, prefer source artifacts over narrative docs.

3. **CLAUDE.md vs current_config conflict on a mutable fact:** Prefer `current_config`. Preserve CLAUDE.md's behavioral rule if one is present. Record the conflict in `unresolved_drift`.

4. **No current_config doc exists for a system:** Treat the relevant source config file (docker-compose.yml, schema.yaml, etc.) as the baseline `current_config`. Do not use CLAUDE.md or README.md runtime claims as authoritative facts.

5. **"Last Updated" manual timestamp in any doc:** Do not treat it as a freshness guarantee. It is not machine-verifiable. Use `last_verified` and `verification_level` in DOC_REGISTRY.yaml as the authoritative staleness signals.

6. **runtime_evidence claim older than 7 days:** Flag it as potentially stale in the task closure `unresolved_drift` field. Verify via the appropriate method (SSH, monitoring dashboard) before acting on it.

---

## Section 5: Closure Output Requirements

Every implementation task (implement_change, operate_or_release) must produce a structured closure summary before the session ends.

```
### Task Closure Summary
- **changed_sources**: [source files modified — YAML, JSON, TypeScript, SQL, etc.]
- **updated_blueprints**: [blueprint docs updated to reflect the change — or "none"]
- **updated_current_docs**: [current_config docs refreshed — or "none"]
- **updated_runtime_evidence**: [runtime_evidence docs updated if runtime behavior changed — or "none"]
- **unresolved_drift**: [discrepancies left open — missing docs, unresolved conflicts, stale claims encountered]
- **roadmap_impact**: [does this change affect phase planning? If yes, which phase?]
- **follow_up_required**: [next tasks needed — including any missing docs that should be created]
```

For audit and review tasks (refresh_current_docs, investigate_runtime_issue), include:
- `evidence_produced` instead of `changed_sources`
- `docs_updated` for any docs modified
- `conflicts_resolved` for any known conflicts now resolved
- `conflicts_remaining` for any conflicts still open

---

## Section 6: Execution Guidelines & Human Handoff

### The Agent Scratchpad
If a task requires more than 3 steps, or if you need to perform complex refactoring, write your intermediate findings, plans, and next steps to `.agent_scratchpad.md` before executing. This prevents losing context and maintains a clear trail of thought.

### Human-Agent Handoff (Interrupts)
If you hit an unresolvable blocker (e.g., a missing dependency, ambiguous architectural choice, or repeated errors you cannot fix), do not spiral into loops or hallucinate solutions. You MUST:
1. Document the current state, blocker, and 2-3 proposed options in `docs/plans/NEEDS_ATTENTION.md`.
2. Cleanly exit and wait for human intervention.

---

## Section 7: Staleness Protocol

1. **"Last Updated" timestamps are advisory only.** They appear in README files and overview docs. They are set manually and are not machine-verifiable. A "Last Updated: YYYY-MM-DD" header does not mean every claim in the document was true on that date.

2. **Authoritative staleness signals** are the `last_verified` and `verification_level` fields in [DOC_REGISTRY.yaml](../reference/registry/DOC_REGISTRY.yaml):
   - `verification_level: none` — no verification has been done; treat all mutable claims as unverified
   - `verification_level: repo_derived` — content was derived from source artifacts in the repo, not live system verification
   - `verification_level: ssh_verified` — claims were verified via live SSH commands (highest available level)

3. **runtime_evidence docs with `last_verified` older than 7 days** should be treated as potentially stale for service health or operational state claims. Record this in the task closure `unresolved_drift` field and re-verify before acting.

4. **When an agent refreshes a doc**, it must update `last_verified` to the current date and set `verification_level` appropriately in DOC_REGISTRY.yaml as part of the closure output.

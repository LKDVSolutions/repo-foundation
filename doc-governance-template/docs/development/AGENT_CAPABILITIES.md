---
doc_id: AGENT_CAPABILITIES
doc_class: active
authority_kind: guide
title: Agent Capabilities & Execution Environment
primary_audience: agents
task_entry_for: []
system_owner: documentation-governance
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- permitted execution tools
- package management environment
- secret access limitations
- git operations
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
# Agent Capabilities & Execution Environment

**doc_id**: AGENT_CAPABILITIES
**doc_class**: active
**authority_kind**: guide
**primary_audience**: agents
**edit_policy**: human

This document defines what AI agents are permitted and technically able to do in this environment.

## 1. Permitted Execution Tools
- **Shell Commands:** Permitted. Agents can run standard Unix shell commands (`bash`, `grep`, `find`, `cat`, etc.).
- **Filesystem Access:** Full read/write access to the repository directory.
- **Network Access:** Permitted for fetching dependencies and documentation.
- **Docker:** Permitted if a `docker-compose.yml` or `Dockerfile` exists.

## 2. Package Management & Environment
- **Python:** `python3`, `pip`. Use `requirements.txt` or `pyproject.toml`.
- **Node.js:** `npm`, `npx`, `yarn` (if lockfiles are present).
- **Other:** Check the repository for specific language toolchains before executing build commands.

## 3. External API & Secret Access
- Agents DO NOT have read access to production secrets.
- Agents MUST NOT execute cloud infrastructure provisioning commands (`terraform apply`, `aws ec2 run-instances`) without explicit human confirmation.
- **Environment Variables**: Always use `dotenv` and read from `.env.local` which is gitignored. NEVER print `os.environ` to the terminal. Rely on `.env.example` to understand the required environment configuration.

## 4. Git Operations
- Agents CAN stage and commit changes locally.
- Agents CAN create new branches.
- Agents CANNOT push to the remote repository `main` or `master` branches without human approval.

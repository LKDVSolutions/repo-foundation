**Directive**: You are waking up in: `[PROJECT_ROOT_PATH]`

Your mission is to perform a **Comprehensive System Audit** of this existing codebase. You must act as a Principal Architect mapping an undocumented system. Your goal is to deeply understand the architecture, data flows, and boundaries, and then formalize that knowledge into the governance framework.

**Phase 1: Discovery (Read-Only)**
Thoroughly investigate the codebase using your file and search tools. Do not make any edits yet.
1. **Identify Entrypoints & Configs**: Locate all `package.json`, `requirements.txt`, `docker-compose.yml`, `Makefile`, `.env.example`, and CI/CD pipeline files.
2. **Map the Architecture**: Identify the frontend, backend, database, caching layers, and any external integrations.
3. **Trace Data Flows**: Find the database schemas, API route definitions, and core business logic services.
4. **Understand Security**: Look for authentication middleware, RBAC implementations, and secret management.

**Phase 2: Formalization (Write)**
Once you have a complete mental model, translate your findings into the following authoritative documents. If a document does not exist, create it (and add it to `DOC_REGISTRY.yaml`).

1. **Update `docs/REFERENCE.md` (Authority Surface Map)**:
   - Document exactly which files own which classes of facts (e.g., "The PostgreSQL schema is authoritative for data models, located in `infra/schema.sql`").
2. **Draft/Update `docs/architecture/OVERVIEW.md`**:
   - Write a high-level summary of the system architecture, primary components, and their interactions.
3. **Draft/Update `docs/reference/current/SERVICE_INVENTORY.md`**:
   - List all running services, their internal/external ports, and their deployment mechanisms based on your reading of the infrastructure files.
4. **Update `DOC_REGISTRY.yaml`**:
   - Ensure all newly created or discovered critical documentation is registered.

**Output format (strict):**
- **architecture_summary**: [1 paragraph high-level description]
- **services_identified**: [List of services]
- **docs_created**: [List of new markdown files]
- **docs_updated**: [List of updated markdown files]
- **blind_spots**: [List any areas of the codebase you could not fully understand or that require human clarification]

**Mandatory Validation:**
Run `python scripts/docs_gate.py --fast` to ensure your documentation additions comply with the registry rules. Fix any failures before completing the task.

# Core Engineering Standards

**doc_id**: ENGINEERING_STANDARDS
**doc_class**: active
**authority_kind**: blueprint
**primary_audience**: both
**edit_policy**: human

---

## 1. The Principle of Idempotency

All automation, infrastructure scripts, and data mutation operations must be **idempotent**. This means an operation should produce the exact same result whether it is executed once or one thousand times.

**Why this is mandatory:**
AI agents and automated pipelines often retry failed commands or re-run scripts. If a script appends to a file without checking if the line exists, or inserts a database record without checking for duplicates, the system state will be corrupted.

**Guardrails:**
- **Scripts:** Always check for existence before creating, and state before mutating (e.g., `mkdir -p`, `CREATE TABLE IF NOT EXISTS`, `grep -q || echo`).
- **APIs:** Implement idempotency keys for POST/PUT requests that mutate critical state.

---

## 2. Infrastructure as Code ("Cattle, Not Pets")

No server, container, or environment should be manually configured. If a production or staging environment dies, the system must be capable of spinning up an identical replacement entirely from version-controlled scripts.

**Why this is mandatory:**
Manual SSH configurations or UI-driven infrastructure changes break the `current_config` authority. If an agent cannot read the infrastructure state from the repository, it cannot safely operate on the system.

**Guardrails:**
- **Zero Manual Configuration:** All environments must be defined via declarative code (e.g., Docker, Terraform, Ansible, Kubernetes manifests).
- **Immutability:** Once deployed, infrastructure components should be replaced rather than modified in place.

---

## 3. "Fail Fast" and Explicit Blast Radiuses

When a system or script encounters an unexpected state, it must crash immediately and loudly rather than attempting to proceed and potentially corrupting data.

**Why this is mandatory:**
AI agents are excellent at writing "happy path" code but can overlook edge cases. If a script fails to connect to a database, it must not proceed to execute a `DROP TABLE` command on an empty connection object.

**Guardrails:**
- **Strict Shell Execution:** All bash scripts must start with `set -euo pipefail`.
- **Defensive Programming:** Validate all inputs at the boundaries. If a required environment variable is missing, raise a fatal error during initialization.
- **Timeouts & Circuit Breakers:** External API calls and database queries must have explicit, short timeouts.

---

## 4. Operational Observability

A system is a black box until it can explain its own internal state. Security logging is defensive, but observability is operational. 

**Why this is mandatory:**
When an AI agent is tasked to `investigate_runtime_issue`, it relies entirely on the telemetry emitted by the system. Without structured data, the agent cannot diagnose the root cause.

**Guardrails:**
- **Structured Logging:** All application logs must be emitted as structured JSON, including trace IDs, timestamps, and severity levels.
- **Health Endpoints:** Every service must expose a `/health` or `/live` HTTP endpoint that validates its internal state and database connectivity.
- **Metrics:** Services should emit standard operational metrics (e.g., Prometheus format) covering request volume, error rates, and latency.

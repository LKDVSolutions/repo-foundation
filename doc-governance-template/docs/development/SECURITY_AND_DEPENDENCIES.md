---
doc_id: SECURITY_AND_DEPENDENCIES
doc_class: active
authority_kind: blueprint
title: Security and Dependency Governance
primary_audience: both
task_entry_for: []
system_owner: security
doc_owner: '[YOUR-NAME]'
updated_by: human
authoritative_for:
- dependency pinning rules
- secret management rules
refresh_policy: manual
verification_level: none
status: active
depends_on: []
---
# Security and Dependency Governance

**doc_id**: SECURITY_AND_DEPENDENCIES
**doc_class**: active
**authority_kind**: blueprint
**primary_audience**: both
**edit_policy**: human

---

## 1. Dependency Management Protocol

AI Agents (LLMs) often suffer from "knowledge cutoff" hallucination, believing that library versions from 1-2 years ago are the "latest". To prevent this, the following rules are mandatory:

### The "No Guessing" Rule
**Agents must never rely on their internal training data to define the "latest" version of a package.** 
When initializing a project or adding a new dependency, the agent MUST use a shell tool to query the live package registry (e.g., `npm view <package> version`, `pip index versions <package>`, or `curl` to the official registry API).

### The "Strict Pinning" Rule
- **No floating versions.** Never use `^`, `~`, `*`, or `latest` in dependency files (`package.json`, `requirements.txt`, etc.).
- **Exact versions only.** Every package must be pinned to a specific, verified version (e.g., `"react": "18.2.0"` not `"react": "^18.2.0"`).
- **Lockfiles are authoritative.** A `package-lock.json`, `poetry.lock`, or `Cargo.lock` must be generated and committed immediately after dependency definition.

---

## 2. Core Security Guardrails

### The "No Hardcoded Secrets" Rule
No API key, private key, JWT secret, database password, or equivalent credential shall ever be written into application code or unencrypted configuration files.
- **Enforcement:** Agents must configure services to load secrets from environment variables (e.g., `os.getenv('DATABASE_URL')`).
- **Documentation:** `.env.example` files must be used to document the *keys* required, with dummy values only (e.g., `API_KEY=your_key_here`).

### The "404 Rule" (Resource Obfuscation)
When implementing multi-tenant or authorization-gated systems, cross-boundary access attempts should return a `404 Not Found` rather than a `403 Forbidden` or `401 Unauthorized` if the existence of the resource itself is sensitive. 

### The "Validate at the Edge" Rule
All external input must be validated at the system edge before being processed by business logic. 
- Use robust validation libraries (e.g., Zod, Pydantic) to define explicit boundaries (max length, allowed characters, format).
- Never trust client-side validation.

---

## 3. Auditing and Updates

- When running the `PROMPT_DEBT_DISCOVERY` routine, agents must explicitly check for violations of these security and dependency rules.
- To update dependencies, agents should use the `PROMPT_DEPENDENCY_BOOTSTRAP` routine to safely query registries and apply updates.

---

## 4. OWASP Top 10 (2025) Integration

Agents must proactively evaluate design decisions, generated code, and proposed architectures against the OWASP Top 10:2025 categories:

### A01:2025 – Broken Access Control
- **Risk:** Attackers bypass authorization to access unauthorized data or functionality (includes SSRF).
- **Mitigation:** Enforce default deny. Implement RBAC/ABAC on the server side. Never trust client-provided IDs or state. Ensure the "404 Rule" is applied for cross-tenant resource requests.

### A02:2025 – Security Misconfiguration
- **Risk:** Insecure default settings, open cloud storage, permissive CORS, or verbose error messages.
- **Mitigation:** Automate infrastructure-as-code (IaC) security scanning. Remove unused features/services. Hardening must be applied to the OS, web server, and application layers.

### A03:2025 – Software Supply Chain Failures
- **Risk:** Vulnerabilities inherited from third-party dependencies, compromised CI/CD pipelines, or unsigned distribution artifacts.
- **Mitigation:** Strictly follow the Dependency Management Protocol in this document. Use lockfiles, audit dependencies regularly, and pin all versions.

### A04:2025 – Cryptographic Failures
- **Risk:** Exposure of sensitive data due to weak algorithms, hardcoded keys, or missing TLS.
- **Mitigation:** Always use TLS for data in transit. Use modern algorithms (e.g., Argon2, scrypt, AES-GCM). Never roll your own crypto or hardcode keys.

### A05:2025 – Injection
- **Risk:** Untrusted data alters the execution of queries or commands (SQLi, NoSQLi, OS injection).
- **Mitigation:** Use parameterized queries or ORMs strictly. Validate at the Edge using strict type-checking and parameterized execution.

### A06:2025 – Insecure Design
- **Risk:** Flaws introduced before coding begins, due to missing threat modeling or insecure architectural patterns.
- **Mitigation:** Require an Architecture Decision Record (ADR) before implementation. Define security boundaries and trust zones explicitly during the design phase.

### A07:2025 – Authentication Failures
- **Risk:** Weak password policies, broken session management, or missing MFA leading to account takeover.
- **Mitigation:** Use established auth providers. Do not deploy custom session management. Enforce strong, expiring sessions and secure cookies (HttpOnly, Secure, SameSite).

### A08:2025 – Software or Data Integrity Failures
- **Risk:** Applications relying on plugins, libraries, or data streams without verifying their integrity (e.g., insecure deserialization).
- **Mitigation:** Validate all digital signatures. Never deserialize untrusted data. Ensure CI/CD pipelines have strict access controls.

### A09:2025 – Security Logging and Alerting Failures
- **Risk:** Failure to log critical security events or missing active alerting, delaying breach detection.
- **Mitigation:** Log all authentication, authorization, and validation failures with sufficient context. Ensure logs do not contain secrets and are monitored actively.

### A10:2025 – Mishandling of Exceptional Conditions (NEW)
- **Risk:** System failures resulting in "fail-open" states or the exposure of sensitive stack traces during error handling.
- **Mitigation:** Ensure applications fail securely ("fail-closed"). Catch all exceptions safely, return generic error messages to clients, and log detailed tracebacks internally.

---

## 5. Microsoft Security Development Lifecycle (SDL) Practices

While many frameworks focus on discovering vulnerabilities, the SDL focuses on baking security in from the start. All development, planning, and architectural decisions must honor these 10 core practices:

1. **Establish security standards, metrics, and governance:** Define the security requirements and quality bars that the software must meet before any code is written.
2. **Require use of proven security features, languages, and frameworks:** Use established, secure-by-design components rather than building custom security logic (e.g., standard auth libraries, ORMs).
3. **Perform security design review and threat modeling:** Identify potential threats and attack vectors early in the design phase (`ARCHITECTURE_DECISION.md`) before writing code.
4. **Define and use cryptography standards:** Ensure that data is protected using industry-standard encryption and hashing algorithms; never roll custom crypto.
5. **Secure the software supply chain:** Manage and verify the security of third-party libraries, open-source components, and dependencies via strict pinning and lockfiles.
6. **Secure the engineering environment:** Protect the tools, build pipelines, and source control systems used to create the software.
7. **Perform security testing:** Use Static Analysis (SAST), Dynamic Analysis (DAST), and dependency audits to find vulnerabilities proactively during development.
8. **Ensure operational platform security:** Secure the underlying infrastructure (cloud, servers, containers) where the code runs, applying least-privilege principles.
9. **Implement security monitoring and response:** Establish mechanisms to detect, investigate, and log security incidents in production.
10. **Provide security training:** Continuously update your knowledge on secure coding guidelines to prevent regressions or the reintroduction of known anti-patterns.

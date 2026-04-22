**Directive**: You are working in: `[PROJECT_ROOT_PATH]`

Your mission is to bootstrap or update the project's dependencies for a `[TECH_STACK_E.G._PYTHON/NODE/GO]` environment. 

**CRITICAL RULE:** Do NOT rely on your internal training memory to guess package versions. Your training data is outdated. You must use live data.

**Phase 1: Discovery (Live Verification)**
Use your shell tools to query the package registry for the actual *current* stable versions of the requested packages.
*Examples:*
- Node: `npm view [package-name] version`
- Python: `pip index versions [package-name]` or `curl -s https://pypi.org/pypi/[package-name]/json | grep '"version"'`

**Target Packages to Verify:**
1. `[PACKAGE_1]`
2. `[PACKAGE_2]`
3. `[PACKAGE_3]`

**Phase 2: Configuration (Strict Pinning)**
1. Generate the dependency file (e.g., `package.json`, `requirements.txt`, `Cargo.toml`).
2. **STRICT PINNING:** You must write exact versions. (e.g., `"fastapi": "0.109.0"`, NOT `"fastapi": "^0.109.0"` or `"fastapi": "*"`)
3. Run the package manager installation command to generate the lockfile (e.g., `npm install`, `poetry lock`, `pip freeze > requirements.txt`).

**Phase 3: Security Validation**
1. Review the generated configuration to ensure no hardcoded secrets or arbitrary execution scripts are included.
2. If the package manager has an audit tool (e.g., `npm audit`, `pip-audit`), run it.

**Output format:**
- **packages_resolved**: [List of packages with their exact live-verified versions]
- **lockfile_generated**: yes/no
- **audit_results**: [Summary of the security audit command]
- **next_steps**: [Actionable next steps for the user]

**Mandatory Validation:**
Run `python scripts/docs_gate.py --fast` to ensure your actions did not break the documentation registry.

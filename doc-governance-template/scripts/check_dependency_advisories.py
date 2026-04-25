#!/usr/bin/env python3
"""Run pip-audit against the pinned Python dependency manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS_PATH = REPO_ROOT / "requirements-dev.txt"


def build_audit_command(requirements_path: Path = REQUIREMENTS_PATH) -> list[str]:
    return [
        sys.executable,
        "-m",
        "pip_audit",
        "-r",
        str(requirements_path),
        "--format",
        "json",
    ]


def _parse_audit_output(raw_output: str) -> Any:
    content = raw_output.strip()
    if not content:
        return None
    return json.loads(content)


def _iter_dependency_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        dependencies = payload.get("dependencies")
        if isinstance(dependencies, list):
            return [item for item in dependencies if isinstance(item, dict)]
    return []


def extract_vulnerabilities(payload: Any) -> list[str]:
    findings: list[str] = []

    for dependency in _iter_dependency_records(payload):
        name = str(dependency.get("name") or "unknown-package")
        version = str(dependency.get("version") or "unknown-version")
        vulnerability_entries = dependency.get("vulns") or dependency.get("vulnerabilities") or dependency.get("advisories") or []
        if not isinstance(vulnerability_entries, list):
            continue

        identifiers: list[str] = []
        for vulnerability in vulnerability_entries:
            if not isinstance(vulnerability, dict):
                continue
            aliases = vulnerability.get("aliases")
            if isinstance(aliases, list) and aliases:
                identifiers.append(str(aliases[0]))
                continue
            for key in ("id", "alias", "name"):
                if vulnerability.get(key):
                    identifiers.append(str(vulnerability[key]))
                    break
            else:
                identifiers.append("UNKNOWN")

        if identifiers:
            findings.append(f"{name}=={version}: {', '.join(sorted(set(identifiers)))}")

    return sorted(findings)


def check_dependency_advisories() -> tuple[int, int, int]:
    passed = 0
    warnings = 0
    failures = 0

    if not REQUIREMENTS_PATH.exists():
        print(f"[FAIL] Dependency manifest not found: {REQUIREMENTS_PATH.name}")
        return passed, warnings, failures + 1

    result = subprocess.run(
        build_audit_command(),
        check=False,
        capture_output=True,
        text=True,
    )

    try:
        payload = _parse_audit_output(result.stdout)
    except json.JSONDecodeError:
        print("[FAIL] pip-audit did not produce valid JSON output")
        if result.stderr.strip():
            print(result.stderr.strip())
        return passed, warnings, failures + 1

    findings = extract_vulnerabilities(payload)
    if findings:
        print(f"[FAIL] Found {len(findings)} dependency advisories in {REQUIREMENTS_PATH.name}")
        for finding in findings:
            print(f"  - {finding}")
        return passed, warnings, failures + 1

    if result.returncode != 0:
        print(f"[FAIL] pip-audit exited with status {result.returncode}")
        if result.stderr.strip():
            print(result.stderr.strip())
        return passed, warnings, failures + 1

    print(f"[PASS] No dependency advisories found in {REQUIREMENTS_PATH.name}")
    return passed + 1, warnings, failures


def main() -> None:
    print("=== check_dependency_advisories.py ===")
    passed, warnings, failures = check_dependency_advisories()
    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
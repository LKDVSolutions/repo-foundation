import subprocess
from unittest.mock import patch

from scripts.check_dependency_advisories import (
    build_audit_command,
    check_dependency_advisories,
    extract_vulnerabilities,
)


def test_build_audit_command_uses_repo_manifest(tmp_path):
    requirements_path = tmp_path / "requirements-dev.txt"

    command = build_audit_command(requirements_path)

    assert command[:3] == [command[0], "-m", "pip_audit"]
    assert command[3:] == ["-r", str(requirements_path), "--format", "json"]


def test_extract_vulnerabilities_reads_dependency_payload():
    payload = {
        "dependencies": [
            {
                "name": "jinja2",
                "version": "3.1.0",
                "vulns": [
                    {"id": "PYSEC-2024-1"},
                    {"aliases": ["GHSA-xxxx-yyyy-zzzz"]},
                ],
            }
        ]
    }

    findings = extract_vulnerabilities(payload)

    assert findings == ["jinja2==3.1.0: GHSA-xxxx-yyyy-zzzz, PYSEC-2024-1"]


def test_check_dependency_advisories_passes_when_no_findings(tmp_path):
    requirements_path = tmp_path / "requirements-dev.txt"
    requirements_path.write_text("pytest==9.0.3\n", encoding="utf-8")

    result = subprocess.CompletedProcess(
        args=["python", "-m", "pip_audit"],
        returncode=0,
        stdout='{"dependencies": []}',
        stderr="",
    )

    with patch("scripts.check_dependency_advisories.REQUIREMENTS_PATH", requirements_path), \
         patch("scripts.check_dependency_advisories.subprocess.run", return_value=result):
        passed, warnings, failures = check_dependency_advisories()

    assert (passed, warnings, failures) == (1, 0, 0)


def test_check_dependency_advisories_fails_when_findings_present(tmp_path):
    requirements_path = tmp_path / "requirements-dev.txt"
    requirements_path.write_text("pytest==9.0.3\n", encoding="utf-8")

    result = subprocess.CompletedProcess(
        args=["python", "-m", "pip_audit"],
        returncode=1,
        stdout='{"dependencies": [{"name": "jinja2", "version": "3.1.0", "vulns": [{"id": "PYSEC-2024-1"}]}]}',
        stderr="",
    )

    with patch("scripts.check_dependency_advisories.REQUIREMENTS_PATH", requirements_path), \
         patch("scripts.check_dependency_advisories.subprocess.run", return_value=result):
        passed, warnings, failures = check_dependency_advisories()

    assert (passed, warnings, failures) == (0, 0, 1)


def test_check_dependency_advisories_fails_when_tool_output_is_invalid(tmp_path):
    requirements_path = tmp_path / "requirements-dev.txt"
    requirements_path.write_text("pytest==9.0.3\n", encoding="utf-8")

    result = subprocess.CompletedProcess(
        args=["python", "-m", "pip_audit"],
        returncode=2,
        stdout='not-json',
        stderr="boom",
    )

    with patch("scripts.check_dependency_advisories.REQUIREMENTS_PATH", requirements_path), \
         patch("scripts.check_dependency_advisories.subprocess.run", return_value=result):
        passed, warnings, failures = check_dependency_advisories()

    assert (passed, warnings, failures) == (0, 0, 1)
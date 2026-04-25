import pytest
from unittest.mock import patch

from scripts.verify_branch_protection import (
    check_branch_protection,
    check_branch_policy,
    detect_provider,
    parse_classic_required_checks,
    parse_ruleset_required_checks,
    resolve_repo_name,
)


def test_parse_classic_required_checks_supports_contexts_and_checks():
    payload = {
        "required_status_checks": {
            "checks": [
                {"context": "doc-gate"},
                {"context": "drift-detection"},
            ]
        }
    }

    contexts = parse_classic_required_checks(payload)

    assert contexts == {"doc-gate", "drift-detection"}


def test_parse_ruleset_required_checks_reads_required_status_rule():
    payload = {
        "rules": [
            {
                "type": "required_status_checks",
                "parameters": {
                    "required_status_checks": [
                        {"context": "doc-gate"},
                        {"context": "dependency-advisory"},
                    ]
                },
            }
        ]
    }

    contexts = parse_ruleset_required_checks(payload)

    assert contexts == {"doc-gate", "dependency-advisory"}


def test_resolve_repo_name_uses_origin_remote_when_env_missing():
    with patch("scripts.verify_branch_protection.os.getenv", return_value=None), \
         patch("scripts.verify_branch_protection.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "git@github.com:LKDVSolutions/repo-foundation.git\n"
        mock_run.return_value.stderr = ""

        repo_name = resolve_repo_name(None)

    assert repo_name == "LKDVSolutions/repo-foundation"


def test_detect_provider_uses_github_env_when_present():
    with patch("scripts.verify_branch_protection.os.getenv", side_effect=lambda key: "LKDVSolutions/repo-foundation" if key == "GITHUB_REPOSITORY" else None):
        provider = detect_provider("auto")

    assert provider == "github"


def test_detect_provider_recognizes_azure_devops_remote():
    with patch("scripts.verify_branch_protection.os.getenv", return_value=None), \
         patch("scripts.verify_branch_protection.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "https://dev.azure.com/example/project/_git/repo\n"
        mock_run.return_value.stderr = ""

        provider = detect_provider("auto")

    assert provider == "azure-devops"


def test_check_branch_protection_fails_when_required_check_missing():
    with patch(
        "scripts.verify_branch_protection.load_required_checks",
        return_value=({"doc-gate", "drift-detection"}, "branch protection"),
    ):
        passed, warnings, failures = check_branch_protection(
            "LKDVSolutions/repo-foundation",
            "main",
            {"doc-gate", "drift-detection", "dependency-advisory"},
        )

    assert (passed, warnings, failures) == (0, 0, 1)


def test_check_branch_protection_warns_on_extra_checks():
    with patch(
        "scripts.verify_branch_protection.load_required_checks",
        return_value=({"doc-gate", "drift-detection", "dependency-advisory", "lint"}, "ruleset"),
    ):
        passed, warnings, failures = check_branch_protection(
            "LKDVSolutions/repo-foundation",
            "main",
            {"doc-gate", "drift-detection", "dependency-advisory"},
        )

    assert (passed, warnings, failures) == (1, 1, 0)


def test_check_branch_policy_warns_for_manual_provider():
    passed, warnings, failures = check_branch_policy(
        "manual",
        {"doc-gate", "drift-detection", "dependency-advisory"},
        None,
        None,
    )

    assert (passed, warnings, failures) == (0, 1, 0)


def test_resolve_repo_name_raises_when_repo_cannot_be_determined():
    with patch("scripts.verify_branch_protection.os.getenv", return_value=None), \
         patch("scripts.verify_branch_protection.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "fatal"

        with pytest.raises(RuntimeError):
            resolve_repo_name(None)
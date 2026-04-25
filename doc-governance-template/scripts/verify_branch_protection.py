#!/usr/bin/env python3
"""Verify default-branch protection against the documented required checks.

GitHub automation is implemented today. Other SCM providers currently fall back to
manual verification guidance instead of failing by default.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REQUIRED_CHECKS = ("doc-gate", "drift-detection", "dependency-advisory")
DEFAULT_PROVIDER = "auto"


def _extract_repo_from_remote(remote_url: str) -> str | None:
    normalized = remote_url.strip()
    if normalized.endswith(".git"):
        normalized = normalized[:-4]

    if normalized.startswith("git@github.com:"):
        return normalized.split(":", 1)[1]
    if normalized.startswith("https://github.com/"):
        return normalized.split("https://github.com/", 1)[1]

    return None


def detect_provider(cli_value: str | None) -> str:
    if cli_value and cli_value != DEFAULT_PROVIDER:
        return cli_value

    env_provider = os.getenv("DOC_GOVERNANCE_SCM_PROVIDER")
    if env_provider:
        return env_provider.strip().lower()

    if os.getenv("GITHUB_REPOSITORY"):
        return "github"

    remote_result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if remote_result.returncode != 0:
        return "manual"

    remote_url = remote_result.stdout.strip().lower()
    if "github.com" in remote_url:
        return "github"
    if "dev.azure.com" in remote_url or "visualstudio.com" in remote_url:
        return "azure-devops"

    return "manual"


def resolve_repo_name(cli_value: str | None) -> str:
    if cli_value:
        return cli_value

    env_repo = os.getenv("GITHUB_REPOSITORY")
    if env_repo:
        return env_repo

    remote_result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if remote_result.returncode == 0:
        repo_name = _extract_repo_from_remote(remote_result.stdout)
        if repo_name:
            return repo_name

    raise RuntimeError("Could not determine GitHub repository name; pass --repo owner/name")


def resolve_branch_name(repo_name: str, cli_value: str | None) -> str:
    if cli_value:
        return cli_value

    env_branch = os.getenv("GITHUB_REF_NAME")
    if env_branch:
        return env_branch

    result = subprocess.run(
        ["gh", "api", f"repos/{repo_name}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Could not resolve default branch via GitHub API; pass --branch explicitly")

    payload = json.loads(result.stdout or "{}")
    branch_name = payload.get("default_branch")
    if not branch_name:
        raise RuntimeError("GitHub API response did not include default_branch")
    return str(branch_name)


def parse_classic_required_checks(payload: dict[str, Any]) -> set[str]:
    required_status_checks = payload.get("required_status_checks") or {}
    checks = required_status_checks.get("checks")
    if isinstance(checks, list) and checks:
        contexts = []
        for item in checks:
            if isinstance(item, dict) and item.get("context"):
                contexts.append(str(item["context"]))
        return set(contexts)

    legacy_contexts = required_status_checks.get("contexts") or []
    return {str(item) for item in legacy_contexts if item}


def parse_ruleset_required_checks(payload: Any) -> set[str]:
    if isinstance(payload, list):
        rules = payload
    elif isinstance(payload, dict):
        rules = payload.get("rules") or []
    else:
        rules = []

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        if rule.get("type") != "required_status_checks":
            continue
        parameters = rule.get("parameters") or {}
        required_checks = parameters.get("required_status_checks") or []
        contexts = []
        for item in required_checks:
            if isinstance(item, dict) and item.get("context"):
                contexts.append(str(item["context"]))
        return set(contexts)
    return set()


def load_required_checks(repo_name: str, branch_name: str) -> tuple[set[str], str]:
    classic = subprocess.run(
        ["gh", "api", f"repos/{repo_name}/branches/{branch_name}/protection"],
        check=False,
        capture_output=True,
        text=True,
    )
    if classic.returncode == 0:
        return parse_classic_required_checks(json.loads(classic.stdout or "{}")), "branch protection"

    ruleset = subprocess.run(
        ["gh", "api", f"repos/{repo_name}/rules/branches/{branch_name}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if ruleset.returncode == 0:
        return parse_ruleset_required_checks(json.loads(ruleset.stdout or "{}")), "ruleset"

    error_output = classic.stderr.strip() or ruleset.stderr.strip() or "GitHub API request failed"
    raise RuntimeError(error_output)


def check_branch_protection(repo_name: str, branch_name: str, required_checks: set[str]) -> tuple[int, int, int]:
    passed = 0
    warnings = 0
    failures = 0

    configured_checks, source_name = load_required_checks(repo_name, branch_name)
    missing_checks = sorted(required_checks - configured_checks)
    extra_checks = sorted(configured_checks - required_checks)

    if missing_checks:
        print(f"[FAIL] {source_name.title()} for {repo_name}@{branch_name} is missing required checks")
        for check_name in missing_checks:
            print(f"  - missing: {check_name}")
        return passed, warnings, failures + 1

    print(f"[PASS] {source_name.title()} for {repo_name}@{branch_name} includes all required checks")
    passed += 1

    if extra_checks:
        print("[WARN] Additional required checks are configured beyond the documented baseline")
        for check_name in extra_checks:
            print(f"  - extra: {check_name}")
        warnings += 1

    return passed, warnings, failures


def check_branch_policy(provider: str, required_checks: set[str], repo_name: str | None, branch_name: str | None) -> tuple[int, int, int]:
    if provider == "github":
        if not repo_name:
            raise RuntimeError("Could not determine GitHub repository name; pass --repo owner/name")
        resolved_branch = branch_name or resolve_branch_name(repo_name, None)
        return check_branch_protection(repo_name, resolved_branch, required_checks)

    checks_text = ", ".join(sorted(required_checks))
    print(f"[WARN] Automated branch-policy verification is not implemented for provider '{provider}'")
    print(f"  Verify manually that the default branch requires equivalent checks: {checks_text}")
    return 0, 1, 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        default=DEFAULT_PROVIDER,
        choices=["auto", "github", "azure-devops", "manual", "other"],
        help="SCM provider to verify. Unsupported providers return a warning for manual verification.",
    )
    parser.add_argument("--repo", help="GitHub repository in owner/name form")
    parser.add_argument("--branch", help="Branch name to verify; defaults to the default branch")
    parser.add_argument(
        "--required-check",
        action="append",
        dest="required_checks",
        help="Required status check name. Repeat to override the default baseline.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    try:
        provider = detect_provider(args.provider)
        required_checks = set(args.required_checks or DEFAULT_REQUIRED_CHECKS)
        repo_name = resolve_repo_name(args.repo) if provider == "github" else None
        branch_name = args.branch if provider != "github" else resolve_branch_name(repo_name, args.branch)
        print("=== verify_branch_protection.py ===")
        passed, warnings, failures = check_branch_policy(provider, required_checks, repo_name, branch_name)
    except RuntimeError as exc:
        print("=== verify_branch_protection.py ===")
        print(f"[FAIL] {exc}")
        print("\nResult: 0 passed, 0 warnings, 1 failures")
        sys.exit(1)

    print(f"\nResult: {passed} passed, {warnings} warnings, {failures} failures")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
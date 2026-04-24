#!/usr/bin/env python3
"""Validate shell scripts enforce fail-fast options."""

from __future__ import annotations

import shlex
from pathlib import Path

try:
    from governance_logger import get_governance_logger
except ImportError:  # pragma: no cover - used when imported as scripts.check_shell_scripts
    from scripts.governance_logger import get_governance_logger

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LOGGER = get_governance_logger("check_shell_scripts.py")

EXCLUDED_DIR_NAMES = {".git", "node_modules", "__pycache__", ".venv", "venv"}
HEADER_LINE_LIMIT = 25


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIR_NAMES for part in path.parts)


def _discover_shell_scripts() -> list[Path]:
    scripts: list[Path] = []
    for file_path in REPO_ROOT.rglob("*.sh"):
        if _is_excluded(file_path):
            continue
        scripts.append(file_path)
    return sorted(scripts)


def _extract_header_lines(content: str) -> list[str]:
    return content.replace("\r\n", "\n").split("\n")[:HEADER_LINE_LIMIT]


def _set_flags_from_line(line: str, state: dict[str, bool]) -> None:
    stripped = line.strip()
    if not stripped.startswith("set "):
        return

    try:
        tokens = shlex.split(stripped)
    except ValueError:
        return

    idx = 1
    while idx < len(tokens):
        token = tokens[idx]

        if token.startswith("-") and token != "-":
            chars = token[1:]
            if "e" in chars:
                state["e"] = True
            if "u" in chars:
                state["u"] = True
            if "o" in chars and idx + 1 < len(tokens) and tokens[idx + 1] == "pipefail":
                state["pipefail"] = True
                idx += 1

        elif token.startswith("+") and token != "+":
            chars = token[1:]
            if "e" in chars:
                state["e"] = False
            if "u" in chars:
                state["u"] = False
            if "o" in chars and idx + 1 < len(tokens) and tokens[idx + 1] == "pipefail":
                state["pipefail"] = False
                idx += 1

        elif token == "-o" and idx + 1 < len(tokens) and tokens[idx + 1] == "pipefail":
            state["pipefail"] = True
            idx += 1
        elif token == "+o" and idx + 1 < len(tokens) and tokens[idx + 1] == "pipefail":
            state["pipefail"] = False
            idx += 1

        idx += 1


def _has_fail_fast_header(content: str) -> bool:
    lines = _extract_header_lines(content)
    state = {"e": False, "u": False, "pipefail": False}
    for line in lines:
        _set_flags_from_line(line, state)
    return state["e"] and state["u"] and state["pipefail"]


def check_shell_scripts() -> tuple[int, int, int]:
    """Validate shell script fail-fast options.

    Returns (passed, warnings, failures).
    """
    passed = 0
    warnings = 0
    failures = 0

    shell_files = _discover_shell_scripts()
    if not shell_files:
        LOGGER.log("INFO", "shell_check_empty", "No shell scripts found", doc_id="ENGINEERING_STANDARDS")
        return passed, warnings, failures

    for script_path in shell_files:
        rel_path = script_path.relative_to(REPO_ROOT)
        try:
            content = script_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warnings += 1
            LOGGER.log("WARN", "shell_decode_warning", f"{rel_path}: non-UTF8 shell script skipped", doc_id="ENGINEERING_STANDARDS")
            continue

        header_line = content.splitlines()[0].strip() if content.splitlines() else ""
        if header_line and not header_line.startswith("#!"):
            warnings += 1
            LOGGER.log("WARN", "shell_shebang_warning", f"{rel_path}: missing shebang header", doc_id="ENGINEERING_STANDARDS")

        if _has_fail_fast_header(content):
            passed += 1
            LOGGER.log("INFO", "shell_check_pass", f"{rel_path}: fail-fast options detected", doc_id="ENGINEERING_STANDARDS")
        else:
            failures += 1
            LOGGER.log("ERROR", "shell_check_fail", f"{rel_path}: missing fail-fast options (-e, -u, pipefail)", doc_id="ENGINEERING_STANDARDS")

    return passed, warnings, failures


def main() -> int:
    passed, warnings, failures = check_shell_scripts()
    LOGGER.log(
        "INFO" if failures == 0 else "ERROR",
        "shell_check_summary",
        f"summary: pass={passed}, warn={warnings}, fail={failures}",
        doc_id="ENGINEERING_STANDARDS",
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

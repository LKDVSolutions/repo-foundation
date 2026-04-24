#!/usr/bin/env python3
"""Schema-aware drift detection framework."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import marko
import yaml
from marko.block import FencedCode

try:
    from governance_logger import get_governance_logger
except ImportError:  # pragma: no cover - used when imported as scripts.detect_drift
    from scripts.governance_logger import get_governance_logger

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
IDEA_INBOX = REPO_ROOT / "docs" / "plans" / "IDEA_INBOX.md"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
COMMENT_BLOCK_RE = re.compile(r"<!--\s*governance:(?P<kind>[a-zA-Z0-9_-]+)\s*(?P<body>.*?)-->", re.DOTALL)

LOGGER = get_governance_logger("detect_drift.py")

CODE_FILE_SUFFIXES = {".py", ".js", ".ts"}
EXCLUDED_CODE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
APPLICATION_CODE_ROOTS = ("src",)


def extract_governance_block(content: str, kind: str) -> list[str]:
    """Extract governed items from markdown using fenced blocks, comments, or prose sections."""
    items: list[str] = []
    target_lang = f"governance:{kind}"

    def _add_items(raw_text: str) -> None:
        for line in raw_text.splitlines():
            clean_line = line.strip()
            if clean_line and not clean_line.startswith("#"):
                items.append(clean_line)

    doc = marko.parse(content)

    def _walk(node) -> None:
        if isinstance(node, FencedCode) and node.extra and target_lang in node.extra:
            text = "".join(child.children for child in node.children)
            _add_items(text)
        if hasattr(node, "children") and isinstance(node.children, list):
            for child in node.children:
                _walk(child)

    _walk(doc)

    for match in COMMENT_BLOCK_RE.finditer(content):
        if match.group("kind") == kind:
            _add_items(match.group("body"))

    if not items:
        lines = content.splitlines()
        in_section = False
        current_level = 0
        section_names = {kind.lower(), f"{kind.lower()}s"}

        for line in lines:
            heading_match = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip().lower()
                if heading_text in section_names:
                    in_section = True
                    current_level = level
                    continue
                if in_section and level <= current_level:
                    break

            if not in_section:
                continue

            bullet_match = re.match(r"^\s*[-*]\s+(.+?)\s*$", line)
            if bullet_match:
                items.append(bullet_match.group(1).strip())
                continue

            if line.strip().startswith("|") and not re.match(r"^\s*\|[-:\s|]+\|\s*$", line):
                columns = [col.strip() for col in line.strip().strip("|").split("|")]
                if columns:
                    items.append(columns[0])

    return sorted(set(items))


def _is_code_file(path: Path) -> bool:
    return path.suffix in CODE_FILE_SUFFIXES and not any(part in EXCLUDED_CODE_DIRS for part in path.parts)


def _iter_application_code_files() -> list[Path]:
    """Return application code files (not governance scripts/tests)."""
    files: set[Path] = set()
    found_roots = False
    for root in APPLICATION_CODE_ROOTS:
        root_path = REPO_ROOT / root
        if root_path.exists() and root_path.is_dir():
            found_roots = True
            for file_path in root_path.rglob("*"):
                if file_path.is_file() and _is_code_file(file_path):
                    files.add(file_path)

    if found_roots:
        return sorted(files)

    for file_path in REPO_ROOT.rglob("*"):
        if not file_path.is_file() or not _is_code_file(file_path):
            continue
        if "scripts" in file_path.parts or "tests" in file_path.parts:
            continue
        files.add(file_path)
    return sorted(files)


def _format_missing_message(adapter_name: str, item_label: str, count: int, source_kind: str, values: list[str]) -> str:
    return f"{adapter_name}: {count} {item_label}(s) in {source_kind}: {values}"


def _contains_forbidden_version_marker(version_spec: str) -> bool:
    forbidden_markers = ("^", "~", ">", "<", "*", "latest", ">=", "<=", "!=", "~=", ",")
    return any(marker in version_spec for marker in forbidden_markers)


def _is_strictly_pinned_requirements_spec(spec: str) -> bool:
    if not spec:
        return False
    if not spec.startswith("=="):
        return False
    return not _contains_forbidden_version_marker(spec[2:])


def _parse_requirement_line(line: str) -> tuple[str, str] | None:
    clean = line.strip()
    if not clean or clean.startswith("#") or clean.startswith("-"):
        return None
    clean = clean.split("#", 1)[0].strip()
    match = re.match(r"^([A-Za-z0-9_.-]+)(.*)$", clean)
    if not match:
        return None
    name = match.group(1)
    spec = match.group(2).strip()
    return name, spec


@dataclass
class DriftReport:
    adapter_name: str
    source_path: Path
    undocumented: list[str] = field(default_factory=list)
    missing_from_source: list[str] = field(default_factory=list)
    item_label: str = "item"

    @property
    def has_drift(self) -> bool:
        return bool(self.undocumented or self.missing_from_source)


class DockerComposeAdapter:
    name = "docker-compose"
    source_file = "docker-compose.yml"
    blueprint_file = "docs/architecture/OVERVIEW.md"
    item_label = "service"

    def extract_services(self, source: Path) -> list[str]:
        try:
            with source.open(encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
        except Exception as exc:
            LOGGER.log("WARN", "docker_parse_error", f"Could not parse {source}: {exc}", doc_id="ARCH_OVERVIEW")
            return []
        return sorted((data.get("services") or {}).keys())

    def extract_documented_services(self, blueprint: Path) -> list[str]:
        return extract_governance_block(blueprint.read_text(encoding="utf-8"), "services")

    def check(self) -> DriftReport | None:
        source = REPO_ROOT / self.source_file
        blueprint = REPO_ROOT / self.blueprint_file
        report = DriftReport(adapter_name=self.name, source_path=source, item_label=self.item_label)

        if not source.exists():
            LOGGER.log("INFO", "adapter_skip", f"{self.name}: {self.source_file} not found", doc_id="ARCH_OVERVIEW")
            return None
        if not blueprint.exists():
            LOGGER.log("WARN", "adapter_skip", f"{self.name}: blueprint {self.blueprint_file} not found", doc_id="ARCH_OVERVIEW")
            return None

        live = set(self.extract_services(source))
        documented = set(self.extract_documented_services(blueprint))
        report.undocumented = sorted(live - documented)
        report.missing_from_source = sorted(documented - live)
        return report


class RequirementsPinAdapter:
    name = "requirements-pin"
    source_files = ("requirements.txt", "package.json", "pyproject.toml")
    blueprint_file = "docs/development/SECURITY_AND_DEPENDENCIES.md"
    item_label = "dependency"

    def _check_requirements_txt(self, path: Path) -> list[str]:
        violations: list[str] = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            parsed = _parse_requirement_line(raw_line)
            if not parsed:
                continue
            name, spec = parsed
            if not _is_strictly_pinned_requirements_spec(spec):
                violations.append(f"{path.name}:{name}{spec}")
        return violations

    def _check_package_json(self, path: Path) -> list[str]:
        violations: list[str] = []
        data = json.loads(path.read_text(encoding="utf-8"))
        sections = ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]
        exact_version_pattern = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9]+)*$")

        for section in sections:
            for pkg, version_spec in (data.get(section) or {}).items():
                spec = str(version_spec).strip()
                if _contains_forbidden_version_marker(spec) or exact_version_pattern.match(spec) is None:
                    violations.append(f"{path.name}:{pkg}:{spec}")
        return violations

    def _check_pyproject(self, path: Path) -> list[str]:
        violations: list[str] = []
        data = tomllib.loads(path.read_text(encoding="utf-8"))

        project = data.get("project") or {}
        for spec in project.get("dependencies") or []:
            spec_str = str(spec)
            if "==" not in spec_str or _contains_forbidden_version_marker(spec_str.replace("==", "", 1)):
                violations.append(f"{path.name}:{spec_str}")

        for group, deps in (project.get("optional-dependencies") or {}).items():
            for spec in deps:
                spec_str = str(spec)
                if "==" not in spec_str or _contains_forbidden_version_marker(spec_str.replace("==", "", 1)):
                    violations.append(f"{path.name}:{group}:{spec_str}")

        poetry_deps = (((data.get("tool") or {}).get("poetry") or {}).get("dependencies") or {})
        exact_version_pattern = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9]+)*$")
        for dep_name, version_data in poetry_deps.items():
            if dep_name == "python":
                continue
            spec = version_data if isinstance(version_data, str) else str(version_data)
            if _contains_forbidden_version_marker(spec) or exact_version_pattern.match(spec) is None:
                violations.append(f"{path.name}:{dep_name}:{spec}")

        return violations

    def extract_unpinned_dependencies(self) -> list[str]:
        violations: list[str] = []
        for source_file in self.source_files:
            path = REPO_ROOT / source_file
            if not path.exists():
                continue
            try:
                if source_file == "requirements.txt":
                    violations.extend(self._check_requirements_txt(path))
                elif source_file == "package.json":
                    violations.extend(self._check_package_json(path))
                elif source_file == "pyproject.toml":
                    violations.extend(self._check_pyproject(path))
            except Exception as exc:
                LOGGER.log("WARN", "dependency_parse_error", f"Could not parse {source_file}: {exc}", doc_id="SECURITY_AND_DEPENDENCIES")
        return sorted(set(violations))

    def check(self) -> DriftReport | None:
        existing_sources = [REPO_ROOT / source_file for source_file in self.source_files if (REPO_ROOT / source_file).exists()]
        blueprint = REPO_ROOT / self.blueprint_file
        report = DriftReport(adapter_name=self.name, source_path=REPO_ROOT, item_label=self.item_label)

        if not existing_sources:
            LOGGER.log("INFO", "adapter_skip", f"{self.name}: no dependency source files found", doc_id="SECURITY_AND_DEPENDENCIES")
            return None
        if not blueprint.exists():
            LOGGER.log("WARN", "adapter_skip", f"{self.name}: blueprint {self.blueprint_file} not found", doc_id="SECURITY_AND_DEPENDENCIES")
            return None

        report.undocumented = self.extract_unpinned_dependencies()
        return report


class EnvVarAdapter:
    name = "env-vars"
    source_file = ".env.example"
    item_label = "env_var"

    def extract_documented_vars(self, source: Path) -> list[str]:
        keys: list[str] = []
        for line in source.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
            if match:
                keys.append(match.group(1))
        return sorted(set(keys))

    def extract_used_vars(self) -> list[str]:
        used: set[str] = set()
        patterns = [
            re.compile(r"os\.getenv\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
            re.compile(r"os\.environ\.get\(\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]"),
            re.compile(r"os\.environ\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]"),
            re.compile(r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
            re.compile(r"process\.env\[\s*['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\s*\]"),
        ]

        for file_path in _iter_application_code_files():
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in patterns:
                for match in pattern.findall(content):
                    used.add(match)

        return sorted(used)

    def check(self) -> DriftReport | None:
        source = REPO_ROOT / self.source_file
        report = DriftReport(adapter_name=self.name, source_path=source, item_label=self.item_label)

        if not source.exists():
            LOGGER.log("WARN", "adapter_skip", f"{self.name}: {self.source_file} not found", doc_id="SECURITY_AND_DEPENDENCIES")
            return None

        documented = set(self.extract_documented_vars(source))
        used = set(self.extract_used_vars())
        report.undocumented = sorted(used - documented)
        return report


class GitHubActionsAdapter:
    name = "github-actions"
    blueprint_file = "docs/architecture/OVERVIEW.md"
    item_label = "dependency"

    def extract_documented_services(self, blueprint: Path) -> list[str]:
        return extract_governance_block(blueprint.read_text(encoding="utf-8"), "services")

    def _normalize_service_name(self, token: str) -> str:
        return token.strip().lower().replace("_", "-")

    def extract_workflow_dependencies(self, workflow_files: list[Path]) -> list[str]:
        dependencies: set[str] = set()
        for workflow_file in workflow_files:
            try:
                data = yaml.safe_load(workflow_file.read_text(encoding="utf-8")) or {}
            except Exception as exc:
                LOGGER.log("WARN", "workflow_parse_error", f"Could not parse {workflow_file}: {exc}", doc_id="ARCH_OVERVIEW")
                continue

            jobs = data.get("jobs") or {}
            for _job_name, job_data in jobs.items():
                if not isinstance(job_data, dict):
                    continue

                for service_name in (job_data.get("services") or {}).keys():
                    dependencies.add(self._normalize_service_name(service_name))

                for env_name in (job_data.get("env") or {}).keys():
                    if env_name.endswith("_URL") or env_name.endswith("_HOST"):
                        dependencies.add(self._normalize_service_name(env_name.rsplit("_", 1)[0]))

            for env_name in (data.get("env") or {}).keys():
                if env_name.endswith("_URL") or env_name.endswith("_HOST"):
                    dependencies.add(self._normalize_service_name(env_name.rsplit("_", 1)[0]))

        return sorted(dependencies)

    def check(self) -> DriftReport | None:
        workflow_files = sorted((REPO_ROOT / ".github" / "workflows").glob("*.y*ml"))
        blueprint = REPO_ROOT / self.blueprint_file
        report = DriftReport(adapter_name=self.name, source_path=REPO_ROOT / ".github" / "workflows", item_label=self.item_label)

        if not workflow_files:
            LOGGER.log("INFO", "adapter_skip", f"{self.name}: no workflow files found", doc_id="ARCH_OVERVIEW")
            return None
        if not blueprint.exists():
            LOGGER.log("WARN", "adapter_skip", f"{self.name}: blueprint {self.blueprint_file} not found", doc_id="ARCH_OVERVIEW")
            return None

        live = set(self.extract_workflow_dependencies(workflow_files))
        documented = {self._normalize_service_name(item) for item in self.extract_documented_services(blueprint)}
        report.undocumented = sorted(live - documented)
        return report


ADAPTERS: list = [
    DockerComposeAdapter(),
    RequirementsPinAdapter(),
    EnvVarAdapter(),
    GitHubActionsAdapter(),
]


def log_drift(message: str) -> None:
    if not IDEA_INBOX.exists():
        LOGGER.log("WARN", "drift_inbox_missing", "IDEA_INBOX.md not found; skipping drift inbox logging", doc_id="IDEA_INBOX")
        return

    content = IDEA_INBOX.read_text(encoding="utf-8")
    entry = f"\n## Automated Drift Report\n**Detected:** {message}\n"
    if entry not in content:
        with IDEA_INBOX.open("a", encoding="utf-8") as handle:
            handle.write(entry)
        LOGGER.log("INFO", "drift_inbox_logged", message, doc_id="IDEA_INBOX")


def _open_issue_exists(title: str) -> bool:
    """Return True if a GitHub issue with this title is already open."""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--search", title, "--state", "open", "--json", "title"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        issues = json.loads(result.stdout or "[]")
        return any(issue.get("title") == title for issue in issues)
    except Exception:
        return False


def create_github_issue(message: str) -> None:
    """Create a GitHub issue for drift. Skips duplicates and auth/tooling failures."""
    title = "Drift Detected"
    try:
        if _open_issue_exists(title):
            LOGGER.log("INFO", "github_issue_skip", f"Open issue '{title}' already exists", doc_id="DRIFT_ISSUE")
            return
        subprocess.run(
            ["gh", "issue", "create", "--title", title, "--body", message],
            check=True,
            capture_output=True,
            timeout=15,
        )
        LOGGER.log("INFO", "github_issue_created", f"Created GitHub issue for drift: {message}", doc_id="DRIFT_ISSUE")
    except FileNotFoundError:
        LOGGER.log("WARN", "github_issue_skip", "gh CLI not available; skipping issue creation", doc_id="DRIFT_ISSUE")
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()[:200]
        LOGGER.log("WARN", "github_issue_skip", f"gh issue create failed (likely auth): {stderr}", doc_id="DRIFT_ISSUE")
    except Exception as exc:
        LOGGER.log("WARN", "github_issue_skip", f"gh issue create error: {exc}", doc_id="DRIFT_ISSUE")


def _extract_evidence_blocks(content: str) -> list[str]:
    """Return raw text of each ```yaml governance:evidence``` fenced block."""
    doc = marko.parse(content)
    blocks: list[str] = []

    def _walk(node) -> None:
        if isinstance(node, FencedCode):
            if node.extra and "governance:evidence" in node.extra:
                blocks.append("".join(child.children for child in node.children))
        if hasattr(node, "children") and isinstance(node.children, list):
            for child in node.children:
                _walk(child)

    _walk(doc)
    return blocks


def _load_agent_config() -> dict:
    config_path = REPO_ROOT / ".agent_config.yaml"
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def check_evidence_freshness() -> tuple[int, int, int]:
    """Check all runtime_evidence docs for structured governance:evidence block freshness."""
    config = _load_agent_config()
    ttl = config.get("governance", {}).get("staleness_ttl", {}).get("runtime_evidence", {})
    warn_days = ttl.get("warn_days", 7)
    fail_days = ttl.get("fail_days", 30)

    passed = warned = failed = 0
    md_files = list(REPO_ROOT.glob("*.md")) + list(REPO_ROOT.glob("docs/**/*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        fm_match = FRONTMATTER_RE.match(content)
        if not fm_match:
            continue

        fm = yaml.safe_load(fm_match.group(1)) or {}
        if fm.get("authority_kind") != "runtime_evidence":
            continue

        rel = md_file.relative_to(REPO_ROOT)
        blocks = _extract_evidence_blocks(content)

        if not blocks:
            LOGGER.log("WARN", "evidence_missing", f"{rel}: runtime_evidence doc has no governance:evidence block", doc_id=fm.get("doc_id", "runtime_evidence"))
            warned += 1
            continue

        now = datetime.now(tz=timezone.utc)
        for block_text in blocks:
            try:
                entries = yaml.safe_load(block_text) or []
            except Exception as exc:
                LOGGER.log("WARN", "evidence_parse_error", f"{rel}: could not parse evidence block: {exc}", doc_id=fm.get("doc_id", "runtime_evidence"))
                warned += 1
                continue

            for entry in entries:
                ts_str = entry.get("timestamp", "")
                if not ts_str:
                    LOGGER.log("WARN", "evidence_timestamp_missing", f"{rel}: evidence entry missing timestamp", doc_id=fm.get("doc_id", "runtime_evidence"))
                    warned += 1
                    continue

                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    LOGGER.log("WARN", "evidence_timestamp_invalid", f"{rel}: invalid timestamp '{ts_str}'", doc_id=fm.get("doc_id", "runtime_evidence"))
                    warned += 1
                    continue

                age_days = (now - ts).days
                cmd = entry.get("command", "?")
                if age_days >= fail_days:
                    LOGGER.log("ERROR", "evidence_stale_fail", f"{rel}: evidence '{cmd}' is {age_days}d old (fail threshold: {fail_days}d)", doc_id=fm.get("doc_id", "runtime_evidence"))
                    failed += 1
                elif age_days >= warn_days:
                    LOGGER.log("WARN", "evidence_stale_warn", f"{rel}: evidence '{cmd}' is {age_days}d old (warn threshold: {warn_days}d)", doc_id=fm.get("doc_id", "runtime_evidence"))
                    warned += 1
                else:
                    LOGGER.log("INFO", "evidence_fresh", f"{rel}: evidence '{cmd}' is {age_days}d old", doc_id=fm.get("doc_id", "runtime_evidence"))
                    passed += 1

    if passed == 0 and warned == 0 and failed == 0:
        LOGGER.log("INFO", "evidence_none", "No runtime_evidence docs found.", doc_id="runtime_evidence")

    return passed, warned, failed


def main() -> int:
    LOGGER.log("INFO", "drift_start", "Starting drift detection", doc_id="DRIFT")

    if not ADAPTERS:
        LOGGER.log("WARN", "drift_no_adapters", "No adapters registered.", doc_id="DRIFT")
        return 0

    total_drift = 0
    for adapter in ADAPTERS:
        LOGGER.log("INFO", "adapter_start", f"Running adapter: {adapter.name}", doc_id="DRIFT")
        report = adapter.check()
        if report is None:
            continue

        if report.has_drift:
            total_drift += 1
            if report.undocumented:
                msg = _format_missing_message(
                    adapter.name,
                    report.item_label,
                    len(report.undocumented),
                    "source not in blueprint",
                    report.undocumented,
                )
                LOGGER.log("ERROR", "drift_detected", msg, doc_id="DRIFT")
                log_drift(msg)
                create_github_issue(msg)

            if report.missing_from_source:
                msg = _format_missing_message(
                    adapter.name,
                    report.item_label,
                    len(report.missing_from_source),
                    "blueprint not in source",
                    report.missing_from_source,
                )
                LOGGER.log("ERROR", "drift_detected", msg, doc_id="DRIFT")
                log_drift(msg)
        else:
            LOGGER.log("INFO", "adapter_pass", f"{adapter.name}: no drift detected", doc_id="DRIFT")

    LOGGER.log("INFO", "drift_summary", f"Drift detection complete. {total_drift} adapter(s) reported drift.", doc_id="DRIFT")
    return 1 if total_drift > 0 else 0


if __name__ == "__main__":
    import sys

    sys.exit(main())

#!/usr/bin/env python3
"""Schema-aware drift detection framework.

Each adapter extracts a normalized inventory from a source artifact.
The engine compares that inventory against what is documented in blueprints.

Blueprint convention: declare governed items in a fenced code block:

    ```yaml governance:services
    web
    db
    worker
    ```

To add a new infrastructure type: implement a new adapter class and register it in ADAPTERS.

Usage:
    python scripts/detect_drift.py
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import marko
import yaml
from marko.block import FencedCode

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
IDEA_INBOX = REPO_ROOT / "docs" / "plans" / "IDEA_INBOX.md"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def extract_governance_block(content: str, kind: str) -> list[str]:
    """Extract items from a structured governance code block using AST parsing.
    
    Looks for:
        ```yaml governance:<kind>
        item1
        item2
        ```
    """
    doc = marko.parse(content)
    
    items = []
    target_lang = f"governance:{kind}"
    
    def _walk(node):
        if isinstance(node, FencedCode):
            if node.extra and target_lang in node.extra:
                # The children of FencedCode are RawText nodes
                text = "".join(child.children for child in node.children)
                # For now we just treat it as a newline separated list of strings
                # In a more advanced implementation, we could parse it as JSON/YAML
                for line in text.splitlines():
                    clean_line = line.strip()
                    if clean_line and not clean_line.startswith("#"):
                        items.append(clean_line)
        
        if hasattr(node, "children") and isinstance(node.children, list):
            for child in node.children:
                _walk(child)
                
    _walk(doc)
    return items


@dataclass
class DriftReport:
    adapter_name: str
    source_path: Path
    undocumented: list[str] = field(default_factory=list)
    missing_from_source: list[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.undocumented or self.missing_from_source)


class DockerComposeAdapter:
    name = "docker-compose"
    source_file = "docker-compose.yml"
    blueprint_file = "docs/architecture/OVERVIEW.md"

    def extract_services(self, source: Path) -> list[str]:
        """Extract service names from docker-compose.yml via YAML parsing."""
        try:
            import yaml
            with open(source, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return list((data or {}).get("services", {}).keys())
        except Exception as e:
            print(f"  [WARN] Could not parse {source}: {e}")
            return []

    def extract_documented_services(self, blueprint: Path) -> list[str]:
        """Extract service names from blueprint using AST parsing."""
        content = blueprint.read_text(encoding="utf-8")
        return extract_governance_block(content, "services")

    def check(self) -> DriftReport | None:
        source = REPO_ROOT / self.source_file
        blueprint = REPO_ROOT / self.blueprint_file
        report = DriftReport(adapter_name=self.name, source_path=source)

        if not source.exists():
            print(f"  [SKIP] {self.name}: {self.source_file} not found — adapter inactive")
            return None
        if not blueprint.exists():
            print(f"  [WARN] {self.name}: blueprint {self.blueprint_file} not found — cannot compare")
            return None

        live = set(self.extract_services(source))
        documented = set(self.extract_documented_services(blueprint))

        report.undocumented = sorted(live - documented)
        report.missing_from_source = sorted(documented - live)
        return report


# Register adapters here. Add KubernetesAdapter, TerraformAdapter, etc. as implemented.
ADAPTERS: list = [DockerComposeAdapter()]


def log_drift(message: str) -> None:
    if not IDEA_INBOX.exists():
        return
    content = IDEA_INBOX.read_text(encoding="utf-8")
    entry = f"\n## Automated Drift Report\n**Detected:** {message}\n"
    if entry not in content:
        with IDEA_INBOX.open("a", encoding="utf-8") as f:
            f.write(entry)
        print(f"  Logged to IDEA_INBOX: {message}")


def _open_issue_exists(title: str) -> bool:
    """Return True if a GitHub issue with this title is already open."""
    try:
        result = subprocess.run(
            ["gh", "issue", "list", "--search", title, "--state", "open", "--json", "title"],
            check=True, capture_output=True, text=True, timeout=15,
        )
        import json
        issues = json.loads(result.stdout or "[]")
        return any(issue.get("title") == title for issue in issues)
    except Exception:
        return False


def create_github_issue(message: str) -> None:
    """Create a GitHub issue for drift. Skips if an open issue with the same title already exists."""
    title = "Drift Detected"
    try:
        if _open_issue_exists(title):
            print(f"  [SKIP] Open GitHub issue '{title}' already exists — skipping duplicate creation")
            return
        subprocess.run(
            ["gh", "issue", "create", "--title", title, "--body", message],
            check=True, capture_output=True, timeout=15
        )
        print("  Created GitHub issue for drift.")
    except FileNotFoundError:
        print("  [SKIP] gh CLI not available — skipping issue creation")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="replace").strip()[:200]
        print(f"  [SKIP] gh issue create failed (likely no auth): {stderr}")
    except Exception as e:
        print(f"  [SKIP] gh issue create error: {e}")


def _extract_evidence_blocks(content: str) -> list[str]:
    """Return raw text of each ```yaml governance:evidence``` fenced block."""
    doc = marko.parse(content)
    blocks: list[str] = []

    def _walk(node):
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
    """Check all runtime_evidence docs for structured governance:evidence block freshness.

    Returns (passed, warned, failed).
    Thresholds come from .agent_config.yaml governance.staleness_ttl.runtime_evidence.
    """
    print("=== check_evidence_freshness ===")
    config = _load_agent_config()
    ttl = (
        config.get("governance", {})
        .get("staleness_ttl", {})
        .get("runtime_evidence", {})
    )
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
            print(f"  [WARN] {rel}: runtime_evidence doc has no structured governance:evidence block")
            warned += 1
            continue

        now = datetime.now(tz=timezone.utc)
        for block_text in blocks:
            try:
                entries = yaml.safe_load(block_text) or []
            except Exception as e:
                print(f"  [WARN] {rel}: could not parse evidence block: {e}")
                warned += 1
                continue

            for entry in entries:
                ts_str = entry.get("timestamp", "")
                if not ts_str:
                    print(f"  [WARN] {rel}: evidence entry missing timestamp")
                    warned += 1
                    continue
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    print(f"  [WARN] {rel}: evidence entry has invalid timestamp '{ts_str}'")
                    warned += 1
                    continue

                age_days = (now - ts).days
                cmd = entry.get("command", "?")
                if age_days >= fail_days:
                    print(f"  [FAIL] {rel}: evidence '{cmd}' is {age_days}d old (fail threshold: {fail_days}d)")
                    failed += 1
                elif age_days >= warn_days:
                    print(f"  [WARN] {rel}: evidence '{cmd}' is {age_days}d old (warn threshold: {warn_days}d)")
                    warned += 1
                else:
                    print(f"  [PASS] {rel}: evidence '{cmd}' is {age_days}d old")
                    passed += 1

    if passed == 0 and warned == 0 and failed == 0:
        print("  [INFO] No runtime_evidence docs found.")

    return passed, warned, failed


def main() -> int:
    print("=== detect_drift.py ===")

    if not ADAPTERS:
        print("No adapters registered. Implement and register an adapter to activate drift detection.")
        return 0

    total_drift = 0
    for adapter in ADAPTERS:
        print(f"\n[Adapter: {adapter.name}]")
        report = adapter.check()
        if report is None:
            continue
        if report.has_drift:
            total_drift += 1
            if report.undocumented:
                msg = (
                    f"{adapter.name}: {len(report.undocumented)} service(s) in source "
                    f"not in blueprint: {report.undocumented}"
                )
                print(f"  [DRIFT] {msg}")
                log_drift(msg)
                create_github_issue(msg)
            if report.missing_from_source:
                msg = (
                    f"{adapter.name}: {len(report.missing_from_source)} service(s) in blueprint "
                    f"not in source: {report.missing_from_source}"
                )
                print(f"  [DRIFT] {msg}")
                log_drift(msg)
        else:
            print("  [PASS] No drift detected")

    print(f"\nDrift detection complete. {total_drift} adapter(s) reported drift.")
    return 1 if total_drift > 0 else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

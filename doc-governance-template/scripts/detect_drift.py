#!/usr/bin/env python3
"""Schema-aware drift detection framework.

Each adapter extracts a normalized inventory from a source artifact.
The engine compares that inventory against what is documented in blueprints.

Blueprint convention: declare governed items in a structured comment block:

    <!-- governance:services
    web
    db
    worker
    -->

To add a new infrastructure type: implement a new adapter class and register it in ADAPTERS.

Usage:
    python scripts/detect_drift.py
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
IDEA_INBOX = REPO_ROOT / "docs" / "plans" / "IDEA_INBOX.md"

# Matches <!-- governance:<kind>\n...\n-->
_GOVERNANCE_BLOCK_RE = re.compile(
    r"<!--\s*governance:(?P<kind>\w+)\s*\n(?P<body>.*?)-->",
    re.DOTALL,
)


def extract_governance_block(content: str, kind: str) -> list[str]:
    """Extract items from a structured governance comment block in a blueprint.

    Looks for:
        <!-- governance:<kind>
        item1
        item2
        -->

    Falls back to scanning prose list items under a heading containing <kind>
    if no structured block is found (backward compatibility).
    """
    for match in _GOVERNANCE_BLOCK_RE.finditer(content):
        if match.group("kind") == kind:
            items = [
                line.strip()
                for line in match.group("body").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            return items

    # Fallback: prose parser — handles h2/h3 headings + bullet lists + table rows
    items: list[str] = []
    in_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,6}\s+", line) and kind in line.lower():
            in_section = True
            continue
        if re.match(r"^#{1,6}\s+", line) and in_section:
            in_section = False
            continue
        if in_section:
            # Bullet list items
            if stripped.startswith(("- ", "* ")):
                items.append(stripped.lstrip("-* ").strip())
            # Markdown table data rows (skip header and separator rows)
            elif stripped.startswith("|") and not re.match(r"^\|[-| ]+\|$", stripped):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if cells and cells[0] and not cells[0].startswith("-"):
                    items.append(cells[0])
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
        """Extract service names from blueprint using structured comment block or prose fallback."""
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

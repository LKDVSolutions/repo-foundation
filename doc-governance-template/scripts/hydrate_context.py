#!/usr/bin/env python3
"""Hydrate the active agent context into `.agent_context.md`.

Run from repo root:
    python scripts/hydrate_context.py [--backlog-item path/to/item.md]
"""

import argparse
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CONTEXT_FILE = REPO_ROOT / ".agent_context.md"

def main():
    parser = argparse.ArgumentParser(description="Hydrate agent context.")
    parser.add_argument("--backlog-item", type=str, help="Path to the active backlog item or task.")
    args = parser.parse_args()

    context_parts = ["# Agent Context\n\nThis file is dynamically generated. Do not edit manually.\n"]
    
    # 1. Load Registry Status Summary
    registry_yaml = REPO_ROOT / "docs" / "reference" / "registry" / "DOC_REGISTRY.yaml"
    if registry_yaml.exists():
        context_parts.append("## Documentation Registry\nStatus: Active. See `docs/reference/registry/DOC_REGISTRY.yaml` for full index.\n")
    
    # 2. Load Top-Level Guardrails
    claude_md = REPO_ROOT / "CLAUDE.md"
    if claude_md.exists():
        context_parts.append("## Top-Level Guardrails (CLAUDE.md)\n")
        context_parts.append(claude_md.read_text(encoding="utf-8"))

    # 3. Load Agent Capabilities
    capabilities_md = REPO_ROOT / "docs" / "development" / "AGENT_CAPABILITIES.md"
    if capabilities_md.exists():
        context_parts.append("\n## Agent Capabilities\n")
        context_parts.append(capabilities_md.read_text(encoding="utf-8"))
        
    # 4. Load Active Task
    if args.backlog_item:
        task_file = Path(args.backlog_item)
        if task_file.exists():
            context_parts.append(f"\n## Active Task ({task_file.name})\n")
            context_parts.append(task_file.read_text(encoding="utf-8"))
        else:
            context_parts.append(f"\n## Active Task\nWarning: Specified task file {task_file} not found.\n")

    CONTEXT_FILE.write_text("\n".join(context_parts), encoding="utf-8")
    print(f"Context hydrated into {CONTEXT_FILE.relative_to(REPO_ROOT)}")

if __name__ == "__main__":
    main()

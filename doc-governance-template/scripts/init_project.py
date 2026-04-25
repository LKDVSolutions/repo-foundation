#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# ANSI colors for terminal output
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{CYAN}{BOLD}=== {text} ==={RESET}\n")

def prompt(text, options=None, default=None):
    if options:
        opt_str = "/".join(options)
        if default:
            opt_str = opt_str.replace(default, f"[{default}]")
        query = f"{text} ({opt_str}): "
    else:
        query = f"{text}: " if not default else f"{text} [{default}]: "
    
    response = input(f"{YELLOW}{query}{RESET}").strip()
    return response if response else default

def replace_placeholders(project_name, author_name, project_description):
    print(f"[{GREEN}*{RESET}] Replacing placeholders across markdown and yaml files...")
    
    # Files to process
    extensions = ['.md', '.yaml', '.yml']
    skip_dirs = ['.git', '.gemini', '__pycache__', 'venv', 'node_modules']
    
    replacements = {
        '[YOUR-PROJECT-NAME]': project_name,
        '[YOUR-NAME]': author_name,
        '[YOUR-PROJECT-DESCRIPTION]': project_description
    }
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                filepath = Path(root) / file
                # Skip this script itself just in case
                if filepath.name == 'init_project.py':
                    continue
                
                try:
                    content = filepath.read_text(encoding='utf-8')
                    modified = False
                    for old, new in replacements.items():
                        if old in content:
                            content = content.replace(old, new)
                            modified = True
                    
                    if modified:
                        filepath.write_text(content, encoding='utf-8')
                        print(f"    Updated {filepath}")
                except Exception as e:
                    print(f"    {RED}Failed to read {filepath}: {e}{RESET}")

def generate_boot_instruction(project_type):
    print(f"[{GREEN}*{RESET}] Generating Agentic Boot Sequence...")
    gemini_dir = Path('.gemini')
    gemini_dir.mkdir(exist_ok=True)
    
    boot_file = gemini_dir / 'boot_instruction.md'
    
    if project_type == 'blank':
        instruction = """# Agentic OS Boot Sequence: Blank Canvas

**Directive:** You are waking up in a new, unconfigured repository. Do NOT write code yet. Do NOT discuss technology stacks.

## Your Mission: Requirement Gathering
You must act as a Senior Product Manager. Your goal is to help the user complete the `docs/plans/templates/PROBLEM_STATEMENT.md`.

1. Read `docs/plans/templates/PROBLEM_STATEMENT.md` to understand the required fields.
2. Ask the user *one question at a time* to extract the "Problem", "Goal", "Audience", and "Constraints".
3. Once you have enough context, draft the `docs/plans/PROBLEM_STATEMENT.md` (removing 'templates/' from the path) and present it to the user for approval.
4. Only after approval, suggest moving to the `ARCHITECTURE_DECISION.md` phase.

**Start now by introducing yourself and asking the user what problem they are trying to solve today.**
"""
    else:
        instruction = """# Agentic OS Boot Sequence: Codebase Retrofit

**Directive:** You are waking up in an existing repository that has just had the Agentic OS Governance framework dropped into it.

## Your Mission: Architectural Audit & Mapping
You must act as a Senior Systems Architect. Your goal is to map the existing codebase into the governance registry.

1. **Audit the Codebase (Safely):** Do NOT do raw `grep` loops over thousands of files. Start by running `python scripts/generate_tree.py` to get a high-level view of the directory structure. Map the repo *one subsystem at a time*. Find package managers (package.json, requirements.txt, etc.), infrastructure configs (docker-compose, terraform), and existing documentation.
2. **Draft the Authority Map:** Update `docs/REFERENCE.md`. Based on what you found, define what files are the authoritative sources for different fact classes (e.g., if you found a docker-compose.yml, it owns 'Service Host Placement').
3. **Register Existing Docs:** Add or update Markdown frontmatter on the most critical existing documents (like the root README, or architecture docs) so they are governed by the system.
4. **Rebuild Registry:** Run `python scripts/aggregate_registry.py` to apply your changes.
5. **Verify Governance:** Run `python scripts/docs_gate.py --fast` to ensure the registry and references are compliant.
6. **Report and Next Steps:** Provide a concise summary of what you found and mapped. Do NOT just stop. You MUST explicitly ask the user what they would like to do next. Provide actionable suggestions, such as:
   - "Would you like me to draft a `PROBLEM_STATEMENT.md` for a new feature?"
   - "Would you like me to analyze any known bugs or technical debt in the files I audited?"
   - "Would you like to review the updated `DOC_REGISTRY.md`?"

**Start now by running `scripts/generate_tree.py`, mapping the core technologies, and guiding the user on their next move.**
"""
    
    boot_file.write_text(instruction, encoding='utf-8')
    print(f"    Created {boot_file}")
    return boot_file

def main():
    print_header("Agentic OS Initialization")
    print("This script will bootstrap the documentation governance framework.")
    
    project_name = prompt("Project Name", default=Path.cwd().name)
    author_name = prompt("Author Name", default=os.getenv('USER', 'agent'))
    project_description = prompt("Project Description", default="Agentic OS managed project.")
    
    print("Are you starting a brand new project, or retrofitting this governance into an existing codebase?")
    print("  [1] Blank Canvas (New Project)")
    print("  [2] Retrofit (Existing Codebase)")
    project_type_input = prompt("Project Type", options=['1', '2'], default='1')
    project_type = 'blank' if project_type_input == '1' else 'retrofit'
    
    print_header("Executing Bootstrap")
    
    replace_placeholders(project_name, author_name, project_description)
    
    print(f"[{GREEN}*{RESET}] Generating initial DOC_REGISTRY.md...")
    subprocess.run([sys.executable, "scripts/aggregate_registry.py"], check=True)
    
    boot_file = generate_boot_instruction(project_type)
    
    print_header("Initialization Complete")
    
    print(f"The passive framework is installed. To wake up the Agentic OS, hand off to your AI.")
    if project_type == 'blank':
        print(f"The agent will interview you to define the project scope.")
    else:
        print(f"The agent will audit your codebase and map the existing architecture.")
        
    print(f"\n{BOLD}To begin the Agentic OS boot sequence, choose one of the following:{RESET}")
    print(f"  {CYAN}Option A (CLI Agent):{RESET} Run {BOLD}gemini \"Read {boot_file} and execute the boot sequence.\"{RESET}")
    print(f"  {CYAN}Option B (Web Agent):{RESET} Copy and paste the contents of {BOLD}{boot_file}{RESET} into ChatGPT, Claude, or another LLM.\n")

if __name__ == '__main__':
    main()

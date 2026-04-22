#!/usr/bin/env python3
import os
import sys

def generate_tree(dir_path, prefix=""):
    """Generates a tree representation of the directory, ignoring certain folders."""
    ignore_dirs = {'.git', '.gemini', '__pycache__', 'venv', 'node_modules', '.claude'}
    
    try:
        entries = sorted(os.listdir(dir_path))
    except PermissionError:
        return

    entries = [e for e in entries if os.path.isdir(os.path.join(dir_path, e)) and e not in ignore_dirs] + \
              [e for e in entries if not os.path.isdir(os.path.join(dir_path, e))]

    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        print(prefix + connector + entry)
        
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            generate_tree(path, prefix + extension)

if __name__ == "__main__":
    print(".")
    generate_tree(".")
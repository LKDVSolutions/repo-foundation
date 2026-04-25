from pathlib import Path


def test_gitignore_does_not_globally_exclude_lockfiles():
    gitignore = Path(__file__).resolve().parent.parent / ".gitignore"
    content = gitignore.read_text(encoding="utf-8")
    patterns = {
        line.strip()
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    assert "*.lock" not in patterns
    assert "*.filelock" in patterns

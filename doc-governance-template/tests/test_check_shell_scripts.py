from pathlib import Path
from unittest.mock import patch

from scripts.check_shell_scripts import _has_fail_fast_header, check_shell_scripts


def _write_shell(tmp_path: Path, rel: str, content: str) -> Path:
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_has_fail_fast_header_exact_line():
    content = "#!/usr/bin/env bash\nset -euo pipefail\necho ok\n"
    assert _has_fail_fast_header(content)


def test_has_fail_fast_header_equivalent_forms():
    content = "#!/usr/bin/env bash\nset -eu\nset -o pipefail\necho ok\n"
    assert _has_fail_fast_header(content)


def test_check_shell_scripts_fails_when_missing_flags(tmp_path):
    _write_shell(tmp_path, "scripts/test.sh", "#!/usr/bin/env bash\nset -e\necho hi\n")

    with patch("scripts.check_shell_scripts.REPO_ROOT", tmp_path), patch("scripts.check_shell_scripts.LOGGER.log"):
        passed, warnings, failures = check_shell_scripts()

    assert passed == 0
    assert warnings == 0
    assert failures == 1


def test_check_shell_scripts_warns_for_missing_shebang(tmp_path):
    _write_shell(tmp_path, "scripts/test.sh", "set -euo pipefail\necho hi\n")

    with patch("scripts.check_shell_scripts.REPO_ROOT", tmp_path), patch("scripts.check_shell_scripts.LOGGER.log"):
        passed, warnings, failures = check_shell_scripts()

    assert passed == 1
    assert warnings == 1
    assert failures == 0

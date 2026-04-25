from scripts.auto_fix import main


def test_auto_fix_is_deprecated(capsys):
	exit_code = main()
	captured = capsys.readouterr()

	assert exit_code == 1
	assert "[DEPRECATED] auto_fix.py is retired." in captured.err

from pathlib import Path

from click.testing import CliRunner
from dodoo_shell.cli import shell

folder = Path(__file__).parent

SHELL_ARGS_A = ""
SHELL_ARGS_B = "--interactive"
SHELL_ARGS_C = "--shell-interface ipython"
SHELL_ARGS_D = "--interactive --uid 2 mydatabase"
SHELL_ARGS_E = (
    f"--uid 2 mydatabase {folder}/data/scripts/without_database.py "
    "scriptarg1 scriptarg2"
)
SHELL_ARGS_INVALID_A = "--uid 2"  # without database
SHELL_ARGS_INVALID_B = "--dry-run"  # without database

WITH_ARGS = f"{folder}/data/scripts/with_args.py"


def test_shell_help():
    runner = CliRunner()
    result = runner.invoke(shell, ["--help"])
    assert result.exit_code == 0


def test_shell(mocker):
    mock = mocker.patch("dodoo_shell.cli._shell")
    runner = CliRunner()
    result = runner.invoke(shell, SHELL_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(shell, SHELL_ARGS_B.split())
    assert result.exit_code == 0
    result = runner.invoke(shell, SHELL_ARGS_C.split())
    assert result.exit_code == 0
    result = runner.invoke(shell, SHELL_ARGS_D.split())
    assert result.exit_code == 0
    result = runner.invoke(shell, SHELL_ARGS_E.split())
    assert result.exit_code == 0

    result = runner.invoke(shell, SHELL_ARGS_INVALID_A.split())
    assert result.exit_code == 1
    result = runner.invoke(shell, SHELL_ARGS_INVALID_B.split())
    assert result.exit_code == 1

    assert mock.call_count == 5

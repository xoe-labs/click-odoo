from click.testing import CliRunner
from dodoo_copy.cli import copy

# might fail unexpectedly if connections exists
COPY_ARGS_A = "existingdb newdb"
# might distrub users temporarily
COPY_ARGS_B = "--force-disconnect existingdb newdb"
COPY_ARGS_C = "-i web -i account --force-disconnect existingdb newdb"


def test_copy_help():
    runner = CliRunner()
    result = runner.invoke(copy, ["--help"])
    assert result.exit_code == 0


def test_copy(mocker):
    mocker.patch("dodoo_copy.cli._copy")
    runner = CliRunner()
    result = runner.invoke(copy, COPY_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(copy, COPY_ARGS_B.split())
    assert result.exit_code == 0
    result = runner.invoke(copy, COPY_ARGS_C.split())
    assert result.exit_code == 0

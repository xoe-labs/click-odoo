from click.testing import CliRunner
from dodoo_init.cli import init, trim_init_cache

INIT_ARGS_A = "-i base -i mail --with-demo mydatabase"
INIT_ARGS_B = "-i base -i mail --no-cache mydatabase"
TRIM_ARGS = "--max-age 5 --max-size 3"


def test_init_help():
    runner = CliRunner()
    result = runner.invoke(init, ["--help"])
    assert result.exit_code == 0


def test_trim_init_cache_help():
    runner = CliRunner()
    result = runner.invoke(trim_init_cache, ["--help"])
    assert result.exit_code == 0


def test_init(mocker):
    mocker.patch("dodoo_init.cli._init")
    runner = CliRunner()
    result = runner.invoke(init, INIT_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(init, INIT_ARGS_B.split())
    assert result.exit_code == 0


def test_trim_init_cache(mocker):
    mocker.patch("dodoo_init.cli._trim_cache")
    runner = CliRunner()
    result = runner.invoke(trim_init_cache, TRIM_ARGS.split())
    assert result.exit_code == 0

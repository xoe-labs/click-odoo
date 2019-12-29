from click.testing import CliRunner
from dodoo_run.cli import bus, cron, graphql, http, queue, run

SERVER_ARGS_A = "127.0.0.1 8080"
SERVER_ARGS_B = "127.0.0.1"
SERVER_FAULTY_ARGS_C = "8080"
SERVER_FAULTY_ARGS_D = "127.0.0.1 808080"


def test_run_help():
    runner = CliRunner()
    result = runner.invoke(run, ["--help"])
    assert result.exit_code == 0


def test_http_help():
    runner = CliRunner()
    result = runner.invoke(http, ["--help"])
    assert result.exit_code == 0


def test_bus_help():
    runner = CliRunner()
    result = runner.invoke(bus, ["--help"])
    assert result.exit_code == 0


def test_graphql_help():
    runner = CliRunner()
    result = runner.invoke(graphql, ["--help"])
    assert result.exit_code == 0


def test_cron_help():
    runner = CliRunner()
    result = runner.invoke(cron, ["--help"])
    assert result.exit_code == 0


def test_queue_help():
    runner = CliRunner()
    result = runner.invoke(queue, ["--help"])
    assert result.exit_code == 0


def test_http(mocker):
    mocker.patch("dodoo_run.cli._http")
    runner = CliRunner()
    result = runner.invoke(http, SERVER_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(http, SERVER_ARGS_B.split())
    assert result.exit_code == 0
    result = runner.invoke(http, SERVER_FAULTY_ARGS_C.split())
    assert result.exit_code != 0
    result = runner.invoke(http, SERVER_FAULTY_ARGS_D.split())
    assert result.exit_code != 0


def test_bus(mocker):
    mocker.patch("dodoo_run.cli._bus")
    runner = CliRunner()
    result = runner.invoke(bus, SERVER_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(bus, SERVER_ARGS_B.split())
    assert result.exit_code == 0
    result = runner.invoke(bus, SERVER_FAULTY_ARGS_C.split())
    assert result.exit_code != 0
    result = runner.invoke(bus, SERVER_FAULTY_ARGS_D.split())
    assert result.exit_code != 0


def test_graphql(graphql_schema, mocker):
    mocker.patch("dodoo_run.cli._graphql")
    runner = CliRunner()
    result = runner.invoke(graphql, [str(graphql_schema)] + SERVER_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(graphql, [str(graphql_schema)] + SERVER_ARGS_B.split())
    assert result.exit_code == 0
    result = runner.invoke(
        graphql, [str(graphql_schema)] + SERVER_FAULTY_ARGS_C.split()
    )
    assert result.exit_code != 0
    result = runner.invoke(
        graphql, [str(graphql_schema)] + SERVER_FAULTY_ARGS_D.split()
    )
    assert result.exit_code != 0


def test_cron(mocker):
    mocker.patch("dodoo_run.cli._cron")
    runner = CliRunner()
    result = runner.invoke(cron, [])
    assert result.exit_code == 0


def test_queue(mocker):
    mocker.patch("dodoo_run.cli._queue")
    runner = CliRunner()
    result = runner.invoke(queue, [])
    assert result.exit_code == 0

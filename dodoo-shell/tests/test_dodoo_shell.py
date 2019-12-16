import logging

import pytest
from dodoo_init import init
from dodoo_shell import ScriptCommitsDuringDryRunError, __version__, environment, shell

params = {  # noqa
    "interactive": False,
    "shell_interface": None,
    "dry_run": False,
    "uid": None,
    "database": None,
    "script": None,
    "script_args": [],
}


def test_version():
    assert __version__ == "0.1.0"


@pytest.fixture
def db(db, newdb, main_loaded):
    modules = ["base"]
    with_demo = True
    no_cache = False
    init(modules, with_demo, no_cache, newdb)
    yield newdb


@pytest.fixture
def scripts(global_datadir):
    yield global_datadir / "scripts"


def has_admin(db):
    with environment(database=db) as global_vars:
        env = global_vars["env"]
        return env["res.users"].search([("login", "=", "admin")])


def has_newadmin(db):
    with environment(database=db) as global_vars:
        env = global_vars["env"]
        return env["res.users"].search([("login", "=", "newadmin")])


def test_validation_logs(caplog, mocker):
    """ Test validation logs errors as expected """
    mocker.patch("dodoo_shell._from_stdin")
    caplog.set_level(logging.ERROR, logger="dodoo_shell.__init__")
    shell(**dict(params, dry_run=True))
    assert len(caplog.records) == 1
    assert f"parameter(s) dry_run require 'database' parameter." in caplog.text
    caplog.clear()
    shell(**dict(params, uid=5))
    assert len(caplog.records) == 1
    assert f"parameter(s) uid require 'database' parameter." in caplog.text


def test_without_script(mocker):
    mock = mocker.patch("dodoo_shell._from_stdin")
    shell(**dict(params))
    assert mock.call_count == 1


def test_script_with_args(capsys, scripts):
    script = scripts / "with_args.py"
    shell(**dict(params, script=script, script_args=["hello world"]))
    captured = capsys.readouterr()
    assert captured.out == "hello world\n"


def test_script_without_database(capsys, scripts, main_loaded):
    """ Test access to non-db local variable """
    script = scripts / "without_database.py"
    shell(**dict(params, script=script))
    captured = capsys.readouterr()
    assert "script - output:" in captured.out


def test_script_with_database_exception(scripts, main_loaded):
    """ Test script failure on access of unavailable variable """
    script = scripts / "with_database.py"
    with pytest.raises(NameError):
        shell(**dict(params, script=script))


def test_environment(db):
    with environment(database=db) as global_vars:
        env = global_vars["env"]
        admin = env["res.users"].search([("login", "=", "admin")])
        assert len(admin) == 1


def test_script_with_database(capsys, db, scripts):
    """ Test access to local variables & environment, and if shell commits """
    script = scripts / "with_database.py"
    shell(**dict(params, script=script, database=db))
    captured = capsys.readouterr()
    assert "script - output:" in captured.out
    assert has_newadmin(db)


def test_dry_run_rollback(capsys, db, scripts):
    """ Test rollback on dry run """
    script = scripts / "with_database.py"
    shell(**dict(params, dry_run=True, database=db, script=script))
    captured = capsys.readouterr()
    assert "script - output:" in captured.out
    assert "admin->newadmin" in captured.out
    assert has_admin(db)


def test_dry_run_exception(db, scripts):
    """ Test exception if script unintendedly commits on dry run """
    script = scripts / "with_commit.py"
    with pytest.raises(ScriptCommitsDuringDryRunError):
        shell(**dict(params, dry_run=True, database=db, script=script))


def test_rollback_in_script(capsys, db, scripts):
    """ Test script and environment rollback can live together """
    script = scripts / "with_rollback.py"
    shell(**dict(params, dry_run=True, database=db, script=script))
    captured = capsys.readouterr()
    assert "script - output:" in captured.out


def test_interactive_without_commit_rollback(capsys, db, scripts, mocker):
    """ test rollback in interactive mode without manual commit """
    mock = mocker.patch("dodoo_shell._from_stdin")
    script = scripts / "with_database.py"
    shell(**dict(params, interactive=True, database=db, script=script))
    assert mock.call_count == 1
    captured = capsys.readouterr()
    assert "script - output:" in captured.out
    assert "admin->newadmin" in captured.out
    assert has_admin(db)


def test_interactive_with_manual_commit(capsys, db, scripts, mocker):
    """ test rollback in interactive mode without manual commit """
    mock = mocker.patch("dodoo_shell._from_stdin")
    script = scripts / "with_commit.py"
    shell(**dict(params, interactive=True, database=db, script=script))
    assert mock.call_count == 1
    captured = capsys.readouterr()
    assert "script - output:" in captured.out
    assert "admin->newadmin" in captured.out
    assert has_newadmin(db)


def test_script_raise_rollback(capsys, db, scripts):
    """ test rollback when script raises """
    script = scripts / "with_raise.py"
    with pytest.raises(RuntimeError) as excinfo:
        shell(**dict(params, database=db, script=script))
    assert "scripterror" in str(excinfo.value)
    assert has_admin(db)


def test_script_raise_commit(capsys, db, scripts):
    """ test rollback when script raises """
    script = scripts / "with_commit_raise.py"
    with pytest.raises(RuntimeError) as excinfo:
        shell(**dict(params, database=db, script=script))
    assert "scripterror" in str(excinfo.value)
    assert has_newadmin(db)


def test_console_no_preferred_shell(capsys, mocker):
    _isatty = mocker.patch("dodoo_shell.console._isatty")
    _isatty.return_value = True
    mock = mocker.patch("dodoo_shell.console.PatchedShell.interact")
    shell(**dict(params))
    mock.assert_called_once_with({"odoo": None}, preferred_shell=None)


def test_console_with_preferred_shell(capsys, mocker):
    _isatty = mocker.patch("dodoo_shell.console._isatty")
    _isatty.return_value = True
    mock = mocker.patch("dodoo_shell.console.PatchedShell.interact")
    shell(**dict(params, shell_interface="ipython"))
    mock.assert_called_once_with({"odoo": None}, preferred_shell="ipython")


def test_stdin(capsys, mocker):
    mock = mocker.patch("dodoo_shell.sys.stdin")
    mock.read.return_value = "print('hello world')"
    shell(**dict(params))
    assert mock.read.call_count == 1
    captured = capsys.readouterr()
    assert "hello world" in captured.out

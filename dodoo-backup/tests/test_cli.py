from click.testing import CliRunner
from dodoo_backup.cli import backup, restore

BACKUP_ARGS_A = "--filestore-include dbname destination-FOLDER"
BACKUP_ARGS_B = "dbname destination-FOLDER"
RESTORE_ARGS_A = "--clear dbname source-FILE"
RESTORE_ARGS_B = "dbname source-FILE"


def test_backup_help():
    runner = CliRunner()
    result = runner.invoke(backup, ["--help"])
    assert result.exit_code == 0


def test_restore_help():
    runner = CliRunner()
    result = runner.invoke(restore, ["--help"])
    assert result.exit_code == 0


def test_backup(mocker):
    mocker.patch("dodoo_init.cli._backup")
    runner = CliRunner()
    result = runner.invoke(backup, BACKUP_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(backup, BACKUP_ARGS_B.split())
    assert result.exit_code == 0


def test_restore(mocker):
    mocker.patch("dodoo_init.cli._restore")
    runner = CliRunner()
    result = runner.invoke(restore, RESTORE_ARGS_A.split())
    assert result.exit_code == 0
    result = runner.invoke(restore, RESTORE_ARGS_B.split())
    assert result.exit_code == 0

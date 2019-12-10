import psycopg2
from click.testing import CliRunner

from dodoo.cli import main


class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0

    def test_framework(self, confd, project_version_file):
        runner = CliRunner()
        args = [
            "--confd",
            str(confd),
            "--framework",
            "../../.odoo",
            str(project_version_file),
            "dummy",
        ]

        @main.command()
        def dummy():
            pass

        result = runner.invoke(main, args)
        # TODO: add database servie to tests
        # At this point we don't have a database yet
        assert isinstance(result.exception, psycopg2.OperationalError)

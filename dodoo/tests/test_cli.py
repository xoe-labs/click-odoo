import pathlib

import psycopg2
from click.testing import CliRunner

from dodoo import RUNMODE
from dodoo.cli import main


class TestCLI:
    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0

    def test_framework(self, confd, project_version_file, framework_dir):
        runner = CliRunner()
        args = [
            "--confd",
            str(confd),
            "--framework",
            str(framework_dir),
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

        import dodoo

        assert dodoo.framework().dodoo_run_mode == RUNMODE.Production
        assert (
            dodoo.framework().dodoo_project_version == project_version_file.read_text()
        )
        o = pathlib.Path(dodoo.framework().__file__)
        h = pathlib.Path(__file__)
        assert h.parents[2] == o.parents[2]

        # Cleanup for later tests during the same session
        dodoo._framework.dodoo_run_mode = None
        dodoo._framework.dodoo_project_version = None
        dodoo._framework.dodoo_config = None
        dodoo._framework = None

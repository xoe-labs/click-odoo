#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the cli entrypoint of the dodoo middleware"""


import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from . import RUNMODE, __version__, main as _main

CONTEXT_SETTINGS = dict(auto_envvar_prefix="DODOO")


@with_plugins(iter_entry_points("dodoo.cli_plugins"))
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-f",
    "--framework",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Path to Odoo framework, if odoo is not in your python path.",
)
@click.option(
    "-c",
    "--confd",
    "config_dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help="Config directory containing json config files for develop, staging & "
    "production. A sane default config is shipped for each env.\n"
    "\tPossible filenames are:\n"
    "\t\todooconfig.prod.json\n"
    "\t\todooconfig.stage.json\n"
    "\t\todooconfig.develop.json\n"
    "\t\tdbconfig.prod.json\n"
    "\t\tdbconfig.stage.json\n"
    "\t\tdbconfig.develop.json\n"
    "\t\tsmtpconfig.prod.json\n"
    "\t\tsmtpconfig.stage.json\n"
    "\t\tsmtpconfig.develop.json\n",
)
@click.option(
    "-h",
    "--call-home",
    "call_home",
    is_flag=True,
    help="Enable Odoo's calling home un-features. (Running code under Odoo's "
    "Enterprise License contracts require you to do so.)",
)
@click.option(
    "-d",
    "--dev",
    "run_mode",
    flag_value=RUNMODE.Develop,
    help="Run in development mode.",
)
@click.option(
    "-s", "--stage", "run_mode", flag_value=RUNMODE.Staging, help="Run in staging mode."
)
@click.option(
    "-p",
    "--prod",
    "run_mode",
    flag_value=RUNMODE.Production,
    default=True,
    help="Run in production mode.",
)
@click.option(
    "-v",
    "--verbose",
    "log_level",
    multiple=True,
    is_flag=True,
    count=True,
    help="Specify the log level from: info, debug. Without: warn.",
)
@click.argument(
    "codeversion",
    type=click.File("r"),
    env="GIT_TAG_FILE",
    help="Specify the version file containing the project's semantic version",
)
@click.version_option(version=__version__)
def main(*args, **kwargs):
    _main(*args, **kwargs)


main.__doc__ = _main.__doc__

if __name__ == "__main__":  # pragma: no cover
    main()

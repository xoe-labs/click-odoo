#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the cli entrypoint of the dodoo middleware"""


import click
import click_pathlib
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from dodoo import RUNMODE, __version__, main as _main

CONTEXT_SETTINGS = dict(auto_envvar_prefix="DODOO")
EPILOG = (
    "All options and arguments can be specified via environment variables "
    "by prefixing their alphanumeric UPPERCASE equivalents with DODOO_.\n"
    "\nExample: DODOO_CODVERSION_FILE"
)


@with_plugins(iter_entry_points("dodoo.cli_plugins"))
@click.group(context_settings=CONTEXT_SETTINGS, help=_main.__doc__, epilog=EPILOG)
@click.option(
    "-f",
    "--framework",
    "framework_dir",
    type=click_pathlib.Path(exists=True, file_okay=False, resolve_path=True),
    help="Path to Odoo framework, if odoo is not in your python path.",
)
@click.option(
    "-c",
    "--confd",
    "config_dir",
    default="./config.d",
    show_default=True,
    type=click_pathlib.Path(exists=True, file_okay=False, resolve_path=True),
    help="Config directory containing json config files for develop, staging & "
    "production. A sane default config is shipped for each env.",
)
@click.option(
    "--log-conf",
    "log_config",
    default=False,
    show_default=True,
    type=click_pathlib.Path(exists=True, file_okay=False, resolve_path=True),
    help="Logger configuration file.",
)
@click.option(
    "-h",
    "--call-home",
    "call_home",
    is_flag=True,
    show_default=True,
    help="Enable Odoo's calling home un-features. (Running code under Odoo's "
    "Enterprise License contracts require you to do so.)",
)
@click.option(
    "-d",
    "--dev",
    "run_mode",
    flag_value=RUNMODE.Develop,
    show_default=True,
    help="Run in development mode.",
)
@click.option(
    "-s",
    "--stage",
    "run_mode",
    flag_value=RUNMODE.Staging,
    show_default=True,
    help="Run in staging mode.",
)
@click.option(
    "-p",
    "--prod",
    "run_mode",
    is_flag=True,
    flag_value=RUNMODE.Production,
    default=True,
    show_default=True,
    help="Run in production mode.",
)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    help="Specify the log level from: info, debug. Without: warn.",
)
@click.argument(
    "projectversion-file",
    type=click_pathlib.Path(exists=True, dir_okay=False, resolve_path=True),
    # help="Specify the version file containing the project's semantic version",
)
@click.version_option(version=__version__)
def main(*args, **kwargs):
    _main(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    main()

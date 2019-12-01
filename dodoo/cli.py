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
)
@click.option(
    "-c",
    "--confd",
    "config_dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.option("-h", "--call-home", "call_home", is_flag=True)
@click.option("-d", "--dev", "run_mode", flag_value=RUNMODE.Develop)
@click.option("-s", "--stage", "run_mode", flag_value=RUNMODE.Staging)
@click.option("-p", "--prod", "run_mode", flag_value=RUNMODE.Production, default=True)
@click.option("-v", "--verbose", "log_level", multiple=True, is_flag=True, count=True)
@click.argument("codeversion", type=click.File("r"), env="GIT_TAG_FILE")
@click.version_option(version=__version__)
def main(*args):
    _main(*args)


main.__doc__ = _main.__doc__

if __name__ == "__main__":  # pragma: no cover
    main()

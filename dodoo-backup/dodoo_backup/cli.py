#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the cli subcommand for dodoo backup & restore"""

import shutil
import sys
import tempfile
from pathlib import Path

import click
import click_pathlib
from dodoo_backup import __version__, backup as _backup, restore as _restore

from dodoo.cli import CONTEXT_SETTINGS, EPILOG


@click.command(context_settings=CONTEXT_SETTINGS, help=_backup.__doc__, epilog=EPILOG)
@click.option(
    "--filestore-include",
    "-f",
    is_flag=True,
    help="Include data files into the backup (zip backup).",
)
@click.argument("dbname")
@click.argument(
    "dest",
    required=False,
    type=click_pathlib.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.version_option(version=__version__)
def backup(*args, **kwargs):
    if not kwargs["dest"]:
        with Path(tempfile.TemporaryDirectory()) as dir:
            kwargs["dest"] = dir
            archive = _backup(*args, **kwargs)
            shutil.copyfileobj(archive, sys.stdout)
    else:
        _backup(*args, **kwargs)


@click.command(context_settings=CONTEXT_SETTINGS, help=_restore.__doc__, epilog=EPILOG)
@click.option(
    "--clear", "-c", is_flag=True, help="Clear database and filestore, if exist."
)
@click.argument("dbname")
@click.argument(
    "src", required=False, type=click_pathlib.Path(exists=True, resolve_path=True)
)
@click.version_option(version=__version__)
def restore(*args, **kwargs):
    if not kwargs["src"]:
        with tempfile.NamedTemporaryFile() as file:
            shutil.copyfileobj(sys.stdin, file)
            kwargs["src"] = Path(file)
            _restore(*args, **kwargs)
    else:
        _restore(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    backup()

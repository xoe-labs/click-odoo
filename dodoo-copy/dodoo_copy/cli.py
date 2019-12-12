#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the cli subcommand for dodoo copy"""

import click
from dodoo_copy import __version__, copy as _copy

from dodoo.cli import CONTEXT_SETTINGS, EPILOG


@click.command(context_settings=CONTEXT_SETTINGS, help=_copy.__doc__, epilog=EPILOG)
@click.option(
    "--install",
    "-i",
    "modules",
    multiple=True,
    show_default=True,
    help="Install addon; specify multiple times.",
)
@click.option(
    "--force-disconnect",
    "-f",
    is_flag=True,
    help="Attempt to disconnect users from the template database.",
)
@click.argument("from-db", required=True)
@click.argument("new-db", required=True)
@click.version_option(version=__version__)
def copy(*args, **kwargs):
    _copy(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    copy()

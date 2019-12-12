#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the cli subcommand for dodoo init"""

import click
from dodoo_init import __version__, init as _init, trim as _trim_cache

from dodoo.cli import CONTEXT_SETTINGS, EPILOG

CACHE_PREFIX_REGEX = r"^[A-Za-z][A-Za-z0-9-]{0,7}$"


@click.command(context_settings=CONTEXT_SETTINGS, help=_init.__doc__, epilog=EPILOG)
@click.option(
    "--install",
    "-i",
    "modules",
    default="base",
    multiple=True,
    show_default=True,
    help="Install addon; specify multiple times.",
)
@click.option("--with-demo", is_flag=True, help="Load Odoo demo data.")
@click.option("--no-cache", is_flag=True, help="Don't use cache.")
@click.argument("database")
@click.version_option(version=__version__)
def init(*args, **kwargs):
    _init(*args, **kwargs)


@click.command(
    context_settings=CONTEXT_SETTINGS, help=_trim_cache.__doc__, epilog=EPILOG
)
@click.option(
    "--max-age",
    default=30,
    show_default=True,
    type=int,
    help="Clear cache after so many days of non-usage." "Use -1 to disable.",
)
@click.option(
    "--max-size",
    default=5,
    show_default=True,
    type=int,
    help="Keep N most recently used cache templates. Use "
    "-1 to disable. Use 0 to empty.",
)
def trim_init_cache(*args, **kwargs):
    _trim_cache(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    init()

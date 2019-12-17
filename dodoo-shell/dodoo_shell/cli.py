#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Credits    : Stéphane Bidoul, Thomas Binsfeld, Benjamin Willig
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the cli subcommand for dodoo shell"""


import click
import click_pathlib
from dodoo_shell import __version__, shell as _shell

from dodoo.cli import CONTEXT_SETTINGS, EPILOG


@click.command(context_settings=CONTEXT_SETTINGS, help=_shell.__doc__, epilog=EPILOG)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Inspect interactively after running the script.",
)
@click.option(
    "--shell-interface",
    help="Preferred shell interface for interactive mode. Accepted "
    "values are ipython, ptpython, bpython, python. If not "
    "provided they are tried in this order.",
)
@click.option("--uid", "-u", type=int, help="Specify a user id (requires database).")
@click.option(
    "--dry-run", is_flag=True, help="Roll back and don't commit (requires database)"
)
@click.argument("database", required=False, type=str)
@click.argument(
    "script", required=False, type=click_pathlib.Path(exists=True, dir_okay=False)
)
@click.argument("script-args", nargs=-1)
@click.version_option(version=__version__)
def shell(*args, **kwargs):
    if not kwargs.get("database") and (kwargs.get("dry_run") or kwargs.get("uid")):
        opts = []
        if kwargs.get("dry_run"):
            opts.append("--dry-run")
        if kwargs.get("uid"):
            opts.append("--uid")
        msg = f"Cli option(s) {','.join(opts)} require 'database' argument."
        raise click.ClickException(msg)
    _shell(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    shell()

#!/usr/bin/env python
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import runpy
import sys

import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from . import commands, console, options

CONTEXT_SETTINGS = dict(auto_envvar_prefix="DODOO")


@with_plugins(iter_entry_points("core_package.cli_plugins"))
@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """Commandline interface for yourpackage."""
    pass


@main.command(cls=commands.CommandWithOdooEnv)
# Run options
@options.db_opt()
@options.addons_path_opt()
@options.rollback_opt()
@click.option(
    "--interactive/--no-interactive",
    "-i",
    help="Inspect interactively after running the script.",
)
@click.option(
    "--shell-interface",
    help="Preferred shell interface for interactive mode. Accepted "
    "values are ipython, ptpython, bpython, python. If not "
    "provided they are tried in this order.",
)
@click.argument("script", required=False, type=click.Path(exists=True, dir_okay=False))
@click.argument("script-args", nargs=-1)
def run(env, interactive, shell_interface, script, script_args):
    """Execute a python script in an initialized Odoo environment. The script
    has access to a 'env' global variable which is an odoo.api.Environment
    initialized for the given database. If no script is provided, the script is
    read from stdin or an interactive console is started if stdin appears to be
    a terminal."""
    global_vars = {"env": env}
    if script:
        sys.argv[1:] = script_args
        global_vars = runpy.run_path(
            script, init_globals=global_vars, run_name="__main__"
        )
    if not script or interactive:
        if console._isatty(sys.stdin):
            if not env:
                click.secho(
                    "No environment set, use `-d dbname` to get one.", fg="white"
                )
            console.Shell.interact(global_vars, shell_interface)
            if env:
                env.cr.rollback()
        else:
            sys.argv[:] = [""]
            global_vars["__name__"] = "__main__"
            exec(sys.stdin.read(), global_vars)

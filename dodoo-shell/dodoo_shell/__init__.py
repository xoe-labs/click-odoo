# =============================================================================
# Created By : David Arnold
# Credits    : Stéphane Bidoul, Thomas Binsfeld, Benjamin Willig
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo shell plugin"""

__version__ = "0.1.0"

import runpy
import sys

import logging

from contextlib import contextmanager
import dodoo
from dodoo.interfaces import odoo

from pathlib import Path

from typing import Optional, List

_log = logging.getLogger(__name__)


class ScriptCommitsDuringDryRunError(Exception):
    pass


def raise_on_commit():
    raise ScriptCommitsDuringDryRunError()


@contextmanager
def environment(
    database: str, uid: int = None, dry_run: bool = False, interactive: bool = False
) -> dict:
    global_vars = {"odoo": dodoo.framework()}
    if not database:
        msg = "No database set; load odoo namespace only."
        _log.info(msg)
        yield global_vars
    else:
        registry = odoo.Registry(database)
        with registry.cursor() as cr:
            orig_commit = cr.commit
            with odoo.Environment(cr, uid=uid) as env:
                ctx = env["res.users"].context_get()
            if dry_run:
                cr.commit = raise_on_commit
            try:
                with odoo.Environment(cr, uid=uid, context=ctx) as env:
                    global_vars.update(env=env, self=env.user)
                    yield global_vars
            except Exception as e:
                cr.rollback()
                raise e
            else:
                cr.rollback() if (dry_run or interactive) else cr.commit()
                cr.commit = orig_commit  # Odoo commits (again) leaving context
        odoo.Database().close_all()


@contextmanager
def args(script_args):
    orig_sys_args = sys.argv
    sys.argv[1:] = script_args
    yield
    sys.argv[:] = orig_sys_args


def _from_stdin(global_vars):
    global_vars["__name__"] = "__main__"
    with args([""]):
        exec(sys.stdin.read(), global_vars)


def shell(
    interactive: bool,
    shell_interface: Optional[str],
    dry_run: bool,
    uid: Optional[int],
    database: Optional[str],
    script: Optional[Path],
    script_args: Optional[List[str]],
) -> None:
    """Run a python script in an initialized Odoo environment. The script
    has access to a 'odoo', 'env' and 'self' (current user) globals.

    If no script is provided, the script is read from stdin or an interactive
    console is started if stdin appears to be a terminal."""

    if not database and dry_run or uid:
        params = []
        if dry_run:
            params.append("dry_run")
        if uid:
            params.append("uid")
        msg = f"parameter(s) {','.join(params)} require 'database' parameter."
        _log.error(msg)

    with environment(database, uid, dry_run, interactive) as global_vars:
        if script:
            with args(script_args):
                global_vars = runpy.run_path(
                    script, init_globals=global_vars, run_name="__main__"
                )
        if not script or interactive:
            from . import console

            if console._isatty(sys.stdin):
                console.PatchedShell.interact(
                    global_vars, preferred_shell=shell_interface
                )
            else:
                _from_stdin(global_vars)

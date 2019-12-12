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

_log = logging.getLogger(__name__)


@contextmanager
def environment(database, uid=None, dry_run=False):
    global_vars = {"odoo": dodoo.framework()}
    if not database:
        msg = "No database set; load odoo namespace only."
        _log.info(msg)
        yield global_vars
    else:
        registry = odoo.Registry(database)
        with registry.cursor() as cr:
            try:
                ctx = odoo.Environment(cr, uid=uid)["res.users"].context_get()
            except Exception as e:
                ctx = {"lang": "en_US"}
                # this happens, for instance, when there are new
                # fields declared on res_partner which are not yet
                # in the database (before -u)
                msg = (
                    "Could not obtain a user context, continuing "
                    "anyway with a default context."
                )
                _log.warning(msg)
                _log.debug(f"Exception was: {e}")
            env = odoo.Environment(cr, uid=uid, context=ctx)
            global_vars.update(env=env, self=env.user)
            yield global_vars
            if dry_run:
                cr.rollback()
            else:
                cr.commit()
        odoo.Database().close_all()


def shell(interactive, shell_interface, dry_run, uid, database, script, script_args):
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

    with environment(database, uid, dry_run) as global_vars:
        if script:
            sys.argv[2:] = script_args
            global_vars = runpy.run_path(
                script, init_globals=global_vars, run_name="__main__"
            )
        if not script or interactive:
            from . import console

            if console._isatty(sys.stdin):
                console.PatchedShell.console(global_vars, shell_interface)
            else:
                sys.argv[:] = [""]
                global_vars["__name__"] = "__main__"
                exec(sys.stdin.read(), global_vars)

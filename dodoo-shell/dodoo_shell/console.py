# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements a patched Odoo Cli Shell class"""

import logging
import os
import sys

from dodoo.interfaces import odoo

_log = logging.getLogger(__name__)

OdooShell = odoo.Cli().shell()


class PatchedShell(OdooShell):
    def __init__(self):
        pass

    def init(self):
        raise NotImplementedError()

    def console(self):
        raise NotImplementedError()

    def shell(self):
        raise NotImplementedError()

    def run(self):
        raise NotImplementedError()

    @classmethod
    def interact(cls, local_vars, preferred_shell=None):
        if preferred_shell:
            shells_to_try = [preferred_shell] + cls.supported_shells
        else:
            shells_to_try = cls.supported_shells

        if "env" not in local_vars:
            print(f"No environment set, use `{sys.argv[0]} shell dbname` to get one.")
        for i in sorted(local_vars):
            print(f"{i}: {local_vars[i]}")

        for shell in shells_to_try:
            try:
                return getattr(cls, shell)(local_vars)
            except ImportError:
                pass
            except Exception:
                _log.error(f"Could not start '{shell}' shell.")
                _log.debug("Shell error:", exc_info=True)

        _log.error("Could not start any shell.")


def _isatty(stream):
    try:
        return os.isatty(stream.fileno())
    except Exception:
        return False

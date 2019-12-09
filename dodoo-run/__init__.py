# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo suck-less odoo server"""


__version__ = "0.0.1"

import logging
import time
import threading
import dodoo.interfaces.odoo as odoo

_log = logging.getLogger(__name__)

# ===================
# Implementation
# ===================


def run(stateless):
    # Logic that implements "stateless"
    pass


def http(*args, **kwargs):
    # Only import the namespace + dependencies, if used
    from .http import http

    http(*args, **kwargs)


def bus(*args, **kwargs):
    # Only import the namespace + dependencies, if used
    from .bus import bus

    bus(*args, **kwargs)


def graphql(*args, **kwargs):
    # Only import the namespace + dependencies, if used
    from .graphql import graphql

    graphql(*args, **kwargs)


def cron():
    for dbname, registry in odoo.Registry.items():
        if registry.ready:
            _log.info(f"run cron jobs on {dbname}")
            thread = threading.currentThread()
            thread.start_time = time.time()
            try:
                odoo.Cron().acquire(dbname)
            except Exception:
                _log.warning(
                    f"running cron jobs on {dbname} raised an Exception:", exc_info=True
                )
    pass

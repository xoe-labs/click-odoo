# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo suck-less (background) workers"""


import logging
import time
import threading
import dodoo.interfaces.odoo as odoo

_log = logging.getLogger(__name__)


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


def queue():
    ...

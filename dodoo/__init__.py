# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo middleware"""


__version__ = "0.0.1"
__all__ = ["RUNMODE", "main"]

import logging
import threading
import os
import enum
import sys


from .config import load_config
from .interfaces import odoo
from .patchers.odoo import Patcher

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    jsonlogger = None

assert sys.version_info >= (3, 7), "doDoo requires Python >= 3.7 to run."

_log = logging.getLogger(__name__)


class RUNMODE(enum.Enum):
    Develop = 1
    Staging = 2
    Production = 3


if jsonlogger:

    class JSONFormatter(jsonlogger.JsonFormatter):
        def format(self, record):
            if record.exc_info:
                mod_name = record.exc_info[0].__module__
                obj_name = record.exc_info[0].__name__
                record.exc_class = f"{mod_name}:{obj_name}"
            record.pid = os.getpid()
            record.dbname = getattr(threading.currentThread(), "dbname", "?")
            return jsonlogger.JsonFormatter.format(self, record)


def main(framework, config_dir, call_home, run_mode, log_level, codeversion):
    """Provides the dodoo common cli entrypoint and sets up the dodoo python
    environment to work, loads the config and sets up logging."""

    logging.setLevel(logging.WARNING - max(log_level, 2) * 10)
    logging.captureWarnings(True)
    config = load_config(config_dir, run_mode)

    # Load odoo module from specified framework path
    if framework:
        sys.path.insert(0, framework)

    # Hold a reference to the global odoo namespace so it's not
    # garbage collected after beeing patched
    global framework
    import odoo as framework

    framework.dodoo_run_mode = run_mode
    framework.dodoo_project_version = codeversion.read().rstrip()

    odoo.Tools.resetlocale()

    # TODO: Review if this is optimal
    if run_mode == RUNMODE.Develop:
        logformat = (
            "%(levelname)s %(dbname)s "
            "%(name)s: %(message)s %(perf_info)s\n"
            "file://%(pathname)s:%(lineno)d"
        )
    else:
        logformat = (
            "%(asctime)s %(levelname)s %(dbname)s "
            "%(name)s: %(message)s %(perf_info)s"
        )
    handler = logging.StreamHandler()
    if handler.isatty():
        formatter = odoo.netscv.ColoredFormatter(logformat)
        perf_filter = odoo.netscv.ColoredPerfFilter()
    elif jsonlogger:
        formatter = JSONFormatter(logformat)
        perf_filter = odoo.netscv.PerfFilter()
    else:
        formatter = odoo.netscv.Formatter(logformat)
        perf_filter = odoo.netscv.PerfFilter()

    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    # TODO: https://www.appdynamics.com/blog/engineering/
    # a-performance-analysis-of-python-wsgi-servers-part-2/
    logging.getLogger("werkzeug").addFilter(perf_filter)

    config.Odoo.apply_log_handler_to(logging)

    if call_home:
        Patcher.features.update(call_home=True)
    Patcher(config.Odoo, config.Db, config.Smtp).apply()

    # Apply configs
    odoo.Config().defaults()
    config.Odoo.apply()
    # config.Db.apply() - completely patched for hotreload
    # config.Smtp.apply() - completely patched for hotreload
    odoo.Modules.initialize_sys_path()

# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo middleware"""


__version__ = "0.0.1"
__all__ = ["RUNMODE", "main", "framework"]

import logging
import colorlog
import threading
import os
import enum
import sys

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


class DBFormatter(logging.Formatter):
    def format(self, record):
        record.pid = os.getpid()
        record.dbname = getattr(threading.current_thread(), "dbname", "?")
        return super().format(record)


class ColoredFormatter(DBFormatter, colorlog.ColoredFormatter):
    pass


if jsonlogger:

    class JSONFormatter(DBFormatter, jsonlogger.JsonFormatter):
        def format(self, record):
            if record.exc_info:
                mod_name = record.exc_info[0].__module__
                obj_name = record.exc_info[0].__name__
                record.exc_class = f"{mod_name}:{obj_name}"
            return super().format(record)


# Those might import RUNMODE
from .configs import load_config  # noqa
from .interfaces import odoo  # noqa
from .patchers.odoo import Patcher  # noqa
from .connections import create_custom_schema_layout  # noqa

_framework = None


def framework():
    return _framework


def main(
    framework_dir, config_dir, call_home, run_mode, log_level, projectversion_file
):
    """Provide the common cli entrypoint, initialize the dodoo python
    environment, load configuration and set up logging.

    Then hand off to a subcommand."""
    rootlogger = logging.getLogger()
    rootlogger.setLevel(logging.WARNING - min(log_level, 2) * 10)
    logging.captureWarnings(True)
    config = load_config(config_dir, run_mode)

    # Load odoo module from specified framework path
    if framework_dir:
        sys.path.insert(0, str(framework_dir))

    # Hold a reference to the global odoo namespace so it's not
    # garbage collected after beeing patched
    global _framework
    import odoo as _framework

    _framework.dodoo_run_mode = run_mode
    _framework.dodoo_project_version = projectversion_file.read().rstrip()

    odoo.Tools().resetlocale()

    # TODO: Review if this is optimal
    if run_mode == RUNMODE.Develop:
        logformat = (
            "%(levelname)s %(dbname)s "
            "%(name)s: %(message)s\n"
            "file://%(pathname)s:%(lineno)d"
        )
    else:
        logformat = "%(asctime)s %(levelname)s %(dbname)s " "%(name)s: %(message)s"
    handler = colorlog.StreamHandler()
    if handler.stream.isatty():
        formatter = ColoredFormatter(
            logformat,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={"message": {"ERROR": "red", "CRITICAL": "red"}},
        )
        perf_filter = odoo.Logging().ColoredPerfFilter()
    elif jsonlogger:
        formatter = JSONFormatter(logformat)
        perf_filter = odoo.Logging().PerfFilter()
    else:
        formatter = DBFormatter(logformat)
        perf_filter = odoo.Logging().PerfFilter()

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
    odoo.Modules().initialize_sys_path()

    # Create database schema layouts on all configured database (if not exists)
    for dsn in list(config.Db.per_dbname_dsn.values()) + [config.Db.default_dsn]:
        create_custom_schema_layout(
            dsn, [config.Db.odoo_schema, config.Db.dodoo_schema]
        )

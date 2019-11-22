#!/usr/bin/env python3
# =============================================================================
# Created By  : David Arnold
# Created Date: 2019-11-20T11:08-05:00
# =============================================================================
"""This module implements the dodoo middleware and it's cli entrypoint"""


__version__ = "0.0.1"
__all__ = [
    "odoo",
    "app",
    "registry",
    "oconn",
    "dconn",
    "config",
    "modules",
    "git",
    "metrics",
    "Patcher",
]

import logging
import threading
import os

import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points


from . import git
from . import metrics
from . import config
from .odoo_patcher import Patcher
from .connection import oconn, dconn

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    jsonlogger = None


_log = logging.getLogger(__name__)


CONTEXT_SETTINGS = dict(auto_envvar_prefix="DODOO")

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


@with_plugins(iter_entry_points("core_package.cli_plugins"))
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("-f", "--framework")
@click.option("-o", "--odoo-config", "odoo_configs", multiple=True)
@click.option("-d", "--db-config", "db_configs", multiple=True)
@click.option("-s", "--stmp-config", "smtp_configs", multiple=True)
@click.option("-h", "--call-home", "call_home", is_flag=True)
@click.option("-v", "--verbose", "log_level", multiple=True, is_flag=True, count=True)
@click.version_option(version=None)
def main(
    framework, odoo_configs, db_configs, smtp_configs, call_home, log_level
):  # noqa: E402
    """Provides the dodoo common cli entrypoint and sets up the dodoo python
    environment to work, loads the config and sets up logging."""

    logging.setLevel(logging.WARNING - max(log_level, 2) * 10)
    logging.captureWarnings(True)

    OdooConfig = config.OdooConfig(odoo_configs)
    DbConfig = config.DbConfig(db_configs)
    SmtpConfig = config.SmtpConfig(smtp_configs)

    # Load odoo module from path
    if framework:
        pass

    # Set up the dodoo namespace (having desired odoo in sys)
    global odoo, app, registry, modules
    import odoo
    from . import app
    from . import registry
    from . import modules

    # Init as per odoo flavours
    odoo.tools.translate.resetlocale()
    odoo.modules.module.initialize_sys_path()

    logformat = (
        "%(asctime)s %(pid)s %(levelname)s %(dbname)s "
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

    for element in OdooConfig.log_handler:
        loggername, level = element.split(":")
        level = getattr(logging, level, logging.INFO)
        logger = logging.getLogger(loggername)
        logger.setLevel(level)
        _log.debug('logger level set: "%s"', element)

    if call_home:
        Patcher.features.update(call_home=True)
    # TODO: Provide a mechanism for dodoo modules to trigger custom features
    # eg.: dodoo-debrand - check what click says about extending command opt
    Patcher(OdooConfig, DbConfig, SmtpConfig).patch()


if __name__ == "__main__":  # pragma: no cover
    main()

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
import sys

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

assert sys.version_info >= (3, 7), "doDoo requires Python >= 3.7 to run."

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


@with_plugins(iter_entry_points("dodoo.cli_plugins"))
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-f",
    "--framework",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.option(
    "-c",
    "--confd",
    "config_dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
)
@click.option("-h", "--call-home", "call_home", is_flag=True)
@click.option("-d", "--dev", "run_mode", flag_value="dev")
@click.option("-s", "--stage", "run_mode", flag_value="stage")
@click.option("-p", "--prod", "run_mode", flag_value="prod", default=True)
@click.option("-v", "--verbose", "log_level", multiple=True, is_flag=True, count=True)
@click.argument("codeversion", type=click.File("r"), env="GIT_TAG_FILE")
@click.version_option(version=None)
def main(framework, config_dir, call_home, run_mode, log_level, codeversion):
    """Provides the dodoo common cli entrypoint and sets up the dodoo python
    environment to work, loads the config and sets up logging."""

    logging.setLevel(logging.WARNING - max(log_level, 2) * 10)
    logging.captureWarnings(True)
    if run_mode == "dev":
        OdooConfig = config.OdooConfigDevelop(config_dir)
        DbConfig = config.DbConfigDevelop(config_dir)
        SmtpConfig = config.SmtpConfigDevelop(config_dir)
    elif run_mode == "stage":
        OdooConfig = config.OdooConfigStage(config_dir)
        DbConfig = config.DbConfigStage(config_dir)
        SmtpConfig = config.SmtpConfigStage(config_dir)
    elif run_mode == "prod":
        OdooConfig = config.OdooConfigProd(config_dir)
        DbConfig = config.DbConfigProd(config_dir)
        SmtpConfig = config.SmtpConfigProd(config_dir)
    else:
        raise Exception()  # Never hit

    # Load odoo module from specified framework path
    if framework:
        sys.path.insert(0, framework)

    # Set up the dodoo namespace (having desired odoo in sys)
    global odoo, app, registry, modules
    import odoo
    from . import app
    from . import registry
    from . import modules

    odoo.release.version[5] = codeversion.read().rstrip()
    odoo.dodoo_run_mode = run_mode

    # Init as per odoo flavours
    odoo.tools.translate.resetlocale()

    if run_mode == "dev":
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

    OdooConfig.apply_log_handler_to(logging)

    Patcher.run_mode = run_mode
    if call_home:
        Patcher.features.update(call_home=True)
    # TODO: Provide a mechanism for dodoo modules to trigger custom features
    # eg.: dodoo-debrand - check what click says about extending command opt
    Patcher(OdooConfig, DbConfig, SmtpConfig).patch()
    odoo.modules.module.initialize_sys_path()


if __name__ == "__main__":  # pragma: no cover
    main()

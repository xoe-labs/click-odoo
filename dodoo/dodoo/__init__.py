# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo middleware"""


__version__ = "0.0.1"
__all__ = ["RUNMODE", "main", "framework"]

import logging
import logging.config
import enum
import sys


from pathlib import Path
from typing import Optional
from dodoo.logger import DEFAULT_LOGGING_CONFIG

_log = logging.getLogger(__name__)

assert sys.version_info >= (3, 7), "doDoo requires Python >= 3.7 to run."


class RUNMODE(enum.Enum):
    Develop = 1
    Staging = 2
    Production = 3


# Those might import RUNMODE
from .configs import load_config  # noqa
from .interfaces import odoo  # noqa
from .patchers.odoo import Patcher  # noqa
from .connections import create_custom_schema_layout  # noqa

_framework = None


def framework():
    return _framework


def main(
    framework_dir: Path,
    config_dir: Path,
    call_home: bool,
    run_mode: RUNMODE,
    verbosity: Optional[int],
    log_config: Optional[Path],
    projectversion_file: Path,
) -> None:
    """Provide the common cli entrypoint, initialize the dodoo python
    environment, load configuration and set up logging.

    Then hand off to a subcommand."""
    if verbosity:
        log_level = logging.WARNING - min(verbosity, 2) * 10
        logging.getLogger("").setLevel(log_level)
        logging.getLogger("odoo").setLevel(log_level)
    if log_config:
        logging.config.fileConfig(log_config)
    else:
        logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
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
    _framework.dodoo_project_version = projectversion_file.read_text().rstrip()
    _framework.dodoo_config = config

    odoo.Tools().resetlocale()

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

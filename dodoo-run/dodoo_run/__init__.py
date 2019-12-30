# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo suck-less odoo server"""


__version__ = "0.1.0"

import logging
import enum
import dodoo

from pathlib import Path

from dodoo import RUNMODE

from .patchers.odoo import SessionStoragePatcher

_log = logging.getLogger(__name__)


class COMPONENT(enum.Enum):
    Http = 1
    Bus = 2
    Graphql = 3
    Cron = 4
    Queue = 5


def _is_dev():
    return dodoo.framework().dodoo_run_mode == RUNMODE.Develop


def http(host: str, port: int) -> None:
    SessionStoragePatcher().apply()
    from .servers import server
    from .servers.http import app as _app

    is_dev = _is_dev()
    app = _app(prod=not is_dev)
    server(app, host, port, prod=not is_dev)


def bus(host: str, port: int) -> None:
    SessionStoragePatcher().apply()
    from .servers import server
    from .servers.bus import app as _app

    is_dev = _is_dev()
    app = _app(prod=not is_dev)
    server(app, host, port, prod=not is_dev)


def graphql(schema: Path, host: str, port: int) -> None:
    SessionStoragePatcher().apply()
    from .servers import server
    from .servers.graphql import app as _app

    is_dev = _is_dev()
    app = _app(schema, prod=not is_dev)
    server(app, host, port, prod=not is_dev)


def cron() -> None:
    from .workers import cron as _cron

    _cron()


def queue() -> None:
    from .workers import queue as _queue

    _queue()

# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo suck-less odoo server"""


__version__ = "0.0.1"

import logging
import enum
import dodoo

from dodoo import RUN_MODE

_log = logging.getLogger(__name__)


class COMPONENT(enum.Enum):
    Http = 1
    Bus = 2
    Graphql = 3
    Cron = 4
    Queue = 5


def _is_dev():
    return dodoo.framework().dodoo_run_mode == RUN_MODE.Develop


def http(host, port):
    from .server import server
    from .server.http import app as _app

    is_dev = _is_dev()
    app = _app(prod=not is_dev)
    server(app, host, port, prod=not is_dev)


def bus(host, port):
    from .server import server
    from .server.bus import app as _app

    is_dev = _is_dev()
    app = _app(prod=not is_dev)
    server(app, host, port, prod=not is_dev)


def graphql(host, port, schema):
    from .server import server
    from .server.graphql import app as _app

    is_dev = _is_dev()
    app = _app(schema, prod=not is_dev)
    server(app, host, port, prod=not is_dev)


def cron():
    from .workers import cron as _cron

    _cron()


def queue():
    from .workers import queue as _queue

    _queue()

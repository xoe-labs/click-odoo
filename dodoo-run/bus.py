# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo suck-less bus server"""

import logging

from prometheus_client import start_http_server
from werkzeug.middleware.proxy_fix import ProxyFix

import dodoo.interfaces.odoo as odoo
from dodoo import RUN_MODE, framework

from .watcher import file_changed

_log = logging.getLogger(__name__)


def bus(host, port):
    global app, watcher, server
    if framework.dodoo_run_mode == RUN_MODE.Develop:
        from werkzeug.serving import run_simple
        from werkzeug.serving import make_ssl_devcert
        import hupper

        hupper.reloader.FileMonitorProxy.file_changed = file_changed
        ssl_context = make_ssl_devcert("/path/to/the/key", host="localhost")
        server = run_simple(
            host,
            port,
            odoo.WSGI().app,
            use_reloader=True,
            ssl_context=ssl_context,
            threaded=True,
        )
    else:
        app = ProxyFix(odoo.WSGI().app)
        import bjoern

        bjoern.listen(app, host, port)
        server = bjoern.listen(app, host, port)
        start_http_server(port + 1)

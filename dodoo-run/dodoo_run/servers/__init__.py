# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo suck-less servers"""

import logging
import uvicorn

from .watcher import file_changed

_log = logging.getLogger(__name__)

server = None


def server(app, host, port, is_dev=False, ssl_keyfile=None, ssl_certfile=None):
    global server

    kwargs = dict(host=host, port=port, log_level="error")

    if is_dev:
        import hupper

        hupper.reloader.FileMonitorProxy.file_changed = file_changed
        hupper.start_reloader(f"{__name__}.run", verbose=False)

    if cert_path:
        kwargs.update(dict(ssl_keyfile=None, ssl_certfile=None))

    server = uvicorn.run(app, **kwargs)

    return server

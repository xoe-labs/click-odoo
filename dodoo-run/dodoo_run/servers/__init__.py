# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo suck-less servers"""

import logging
import uvicorn

from starlette.types import ASGIApp
from .watcher import file_changed

from ._common import resolve_devcert


_log = logging.getLogger(__name__)

server = None


def server(app: ASGIApp, host: str, port: int, is_dev: bool = False) -> "server":
    global server

    kwargs = dict(host=host, port=port, log_level="error")

    if is_dev:
        import hupper

        hupper.reloader.FileMonitorProxy.file_changed = file_changed
        hupper.start_reloader(f"{__name__}.run", verbose=False)
        kwargs.update(resolve_devcert())

    server = uvicorn.run(app, **kwargs)

    return server

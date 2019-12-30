# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo suck-less servers"""

import dodoo
import logging
import uvicorn

from starlette.types import ASGIApp

_log = logging.getLogger(__name__)

server = None


def server(app: ASGIApp, host: str, port: int, prod: bool = True) -> "server":
    global server

    kwargs = dict(host=host, port=port, log_level="debug", debug=True)

    if not prod:
        odooconfig = dodoo.framework().dodoo_config.Odoo
        assert odooconfig.ssl_keyfile and odooconfig.ssl_certfile
        kwargs.update(
            ssl_keyfile=str(odooconfig.ssl_keyfile),
            ssl_certfile=str(odooconfig.ssl_certfile),
        )

    server = uvicorn.run(app, **kwargs)

    return server

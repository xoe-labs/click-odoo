# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo suck-less bus server"""

import logging

from dodoo_run.middleware.globalscope import GlobalScopeAccessorMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.routing import Route
from starlette.types import ASGIApp
from starlette_prometheus import PrometheusMiddleware, metrics

import dodoo.interfaces.odoo as odoo

from ._common import GZipMiddlewareArgs, SessionMiddlewareArgs

_log = logging.getLogger(__name__)


def middleware(prod):
    return [
        Middleware(HTTPSRedirectMiddleware),
        Middleware(SessionMiddleware, **SessionMiddlewareArgs),
        Middleware(WSGIMiddleware, workers=1),
        Middleware(GZipMiddleware, **GZipMiddlewareArgs),
        Middleware(GlobalScopeAccessorMiddleware),
    ] + ([Middleware(PrometheusMiddleware)] if prod else [])


def routes(prod):
    return [Route("/longpolling", endpoint=odoo.WSGI().app)] + (
        [Route("/metrics", endpoint=metrics)] if prod else []
    )


def app(prod: bool) -> ASGIApp:
    app = Starlette(middleware=middleware(prod), routes=routes(prod), debug=not prod)
    return app

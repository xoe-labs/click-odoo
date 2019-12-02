# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo suck-less graphql server"""

import importlib
import logging

import uvicorn
from dodoo_run.middleware.odoo import (
    OdooBasicAuthBackendAsync,
    OdooEnvironmentMiddlewareAsync,
)
from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from strawberry.asgi import GraphQL

from dodoo import RUN_MODE, framework

_log = logging.getLogger(__name__)


def graphql(host, port, schema):

    middleware = [
        Middleware(HTTPSRedirectMiddleware),
        Middleware(SessionMiddleware),
        Middleware(AuthenticationMiddleware, backend=OdooBasicAuthBackendAsync()),
        Middleware(OdooEnvironmentMiddlewareAsync),
        Middleware(GZipMiddleware, minimum_size=500),
    ]
    schema_module = importlib.import_module(schema)

    global app, server
    if framework.dodoo_run_mode == RUN_MODE.Develop:
        app = Starlette(middleware=middleware, debug=True)
        graphql_app = requires("authenticated")(
            GraphQL(schema_module.schema, debug=True)
        )
    else:
        app = Starlette(middleware=middleware)
        graphql_app = requires("authenticated")(GraphQL(schema_module.schema))

    # pip install starlette-prometheus
    try:
        from starlette_prometheus import metrics, PrometheusMiddleware
    except ImportError:
        pass
    else:
        app.add_middleware(PrometheusMiddleware)
        app.add_route("/metrics/", metrics)

    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)
    uvicorn.run(app, host=host, port=port, log_level="error")

# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements odoo asgi middleware to provide an Odoo Environment
for http and websocket transport"""

import typing

from starlette import status
from starlette.requests import HTTPConnection
from starlette.responses import PlainTextResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

import dodoo.interfaces.odoo as odoo


class OdooEnvHTTPConnection(HTTPConnection):
    """
    A class for incoming Odoo HTTP connections, that is used to provide
    any odoo specific functionality that is common to both `Request` and
    `WebSocket`.
    """

    @property
    def env(self) -> typing.Any:
        assert (
            "env" in self.scope
        ), "OdooEnvironmentMiddleware must be installed to access request.env"
        return self.scope["env"]


class OdooEnvironmentMiddlewareAsync:
    """
    A middleware class that lazily initializes an Odoo Environment.
    """

    def __init__(
        self,
        app: ASGIApp,
        on_error: typing.Callable[[HTTPConnection, Exception], Response] = None,
    ) -> None:
        self.app = app
        self.on_error = (
            on_error if on_error is not None else self.default_on_error
        )  # type: typing.Callable[[HTTPConnection, Exception], Response]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        conn = HTTPConnection(scope)

        if conn.user.is_authenticated:
            try:
                scope["env"] = odoo.Tools.lazy(
                    odoo.Environment(
                        odoo.Tools.lazy(odoo.Registry(conn.user.database)),
                        conn.user.uid,
                    )
                )
            except Exception as exc:
                response = self.on_error(conn, exc)

                if scope["type"] == "websocket":
                    await send({"type": "websocket.close", "code": 1011})
                else:
                    await response(scope, receive, send)
                return
        await self.app(scope, receive, send)

    @staticmethod
    def default_on_error(conn: HTTPConnection, exc: Exception) -> Response:
        return PlainTextResponse(
            str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

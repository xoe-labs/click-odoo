# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements a global scope accessor for asgi"""

from starlette.types import ASGIApp, Receive, Scope, Send

import contextvars

scope = contextvars.ContextVar("scope")


class GlobalScopeAccessorMiddleware:
    """
    A middleware class that exports scope to arbitrarily access it.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        token = scope.set(scope)
        await self.app(scope, receive, send)
        scope.reset(token)

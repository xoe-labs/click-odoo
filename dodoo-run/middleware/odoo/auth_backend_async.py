# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements odoo asgi middleware to provide an authentication
backend for the authentication middleware"""

import binascii
import typing
from base64 import b64decode

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
    UnauthenticatedUser,
)
from starlette.reqeusts import HTTPConnection

import dodoo.interfaces.odoo as odoo


class OdooUser(BaseUser):
    def __init__(self, login: str, database: str, uid: int) -> None:
        self.login = login
        self.database = database
        self.uid = uid

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return f"{self.database}:{self.login}"


class OdooBasicAuthBackendAsync(AuthenticationBackend):
    async def authenticate(
        self, conn: HTTPConnection
    ) -> typing.Optional[typing.Tuple["AuthCredentials", "OdooUser"]]:
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "basic":
                return
            decoded = b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        database, _, login, _, password = decoded.partition(":")
        try:
            uid = odoo.Authentication().authenticate(database, login, password)
            scopes = ["authenticated", database]
            return AuthCredentials(scopes), OdooUser(login, database, uid)
        except odoo.Exceptions().AccessDenied:
            return AuthCredentials(), UnauthenticatedUser()

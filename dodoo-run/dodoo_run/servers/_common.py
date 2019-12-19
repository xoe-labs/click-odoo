# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the common data accessors shared among servers"""

from starlette.datastructures import Secret

import dodoo

SessionDataKey = "session_data"


class SessionSecret(Secret):
    """
    Resolves to a string value that should not be revealed in tracebacks etc.
    You should cast the value to `str` at the point it is required.
    """

    def __init__(self):
        pass

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}('**********')"

    def __str__(self) -> str:
        return dodoo.dodoo_config.Odoo.Sec.session_encryption_key


SessionMiddlewareArgs = dict(
    sekret_key=SessionSecret(), session_cookie=SessionDataKey, https_only=True
)
GZipMiddlewareArgs = dict(minimum_size=500)


def resolve_devcert():
    ssl_keyfile = dodoo.dodoo_config.Odoo.ssl_keyfile
    ssl_certfile = dodoo.dodoo_config.Odoo.ssl_certfile
    assert ssl_keyfile and ssl_certfile
    return dict(ssl_keyfile=str(ssl_keyfile), ssl_certfile=str(ssl_certfile))

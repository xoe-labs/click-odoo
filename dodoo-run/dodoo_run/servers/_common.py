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

    def __str__(self) -> str:
        f = dodoo.framework()
        return f.dodoo_config.Odoo.Sec.session_encryption_key


SessionMiddlewareArgs = dict(
    secret_key=SessionSecret(), session_cookie=SessionDataKey, https_only=True
)

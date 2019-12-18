# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements odoo wasgi / asgi middleware"""

from .environment_async import OdooEnvironmentMiddlewareAsync  # noqa
from .auth_backend_async import OdooBasicAuthBackendAsync  # noqa

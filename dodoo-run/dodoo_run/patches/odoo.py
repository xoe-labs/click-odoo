# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements a monkey patcher scoped for use with dodoo run"""

from dodoo_run.middleware.globalscope import scope

from dodoo.interfaces import odoo
from dodoo.patchers import BasePatcher

from ..interfaces import _odoo
from ..sessions import ClientSessionStore


class OdooClientSessionStore(ClientSessionStore):
    """Modified Odoo client session store. Provides the path interface for
    session.save_request_data / session.load_request_data methods of the
    Odoo Session Class.
    """

    def __init__(self, session_class=_odoo.Session().SessionClass, **kwargs):
        super().__init__(**kwargs)
        self.path = odoo.Config().session_dir()


# Inheriting order important
class SessionStoragePatcher(_odoo.Patchable, BasePatcher):
    def session_store(self):
        return OdooClientSessionStore(scope=scope.get())

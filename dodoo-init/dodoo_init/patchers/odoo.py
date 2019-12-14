# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements a monkey patcher scoped for use with dodoo init"""

from dodoo.patchers import BasePatcher

from ..interfaces import odoo


# Inheriting order important
class AttachmentStoragePatcher(odoo.Patchable, BasePatcher):
    def _storage(self):
        return lambda: "db"

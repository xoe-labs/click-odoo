# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements an interface to the odoo namespace.
Hence, maintainers have a single source of truth of it's usage.
Consequent lazy loading of patchable properties ensures patchability.
For consistency, never access the odoo namespace directly."""

from dodoo.patchers import PatchableProperty as PProp


class Patchable:

    # #############################
    # Index of patched namespaces #
    # #############################
    #
    # odoo.addons.base
    #
    # #############################

    # odoo.addons.base
    _storage = PProp("odoo.addons.base.models.ir_attachment:IrAttachment._storage")

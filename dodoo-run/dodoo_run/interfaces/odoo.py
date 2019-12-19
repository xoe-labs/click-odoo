# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements an interface to the odoo namespace.
Hence, maintainers have a single source of truth of it's usage.
Consequent lazy loading of patchable properties ensures patchability.
For consistency, never access the odoo namespace directly."""

from importlib import import_module

from dodoo.patchers import PatchableProperty as PProp


class Session:
    def __init__(self):
        self._r = import_module("odoo.http")

    @property
    def SessionClass(self):
        return self._r.OpenERPSession


class Patchable:

    # #############################
    # Index of patched namespaces #
    # #############################
    #
    # odoo.http
    #
    # #############################

    # odoo.http
    session_gc = PProp("odoo.http:session_gc")
    session_store = PProp("odoo.http:Root.session_store")

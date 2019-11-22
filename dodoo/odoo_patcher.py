#!/usr/bin/env python3
# =============================================================================
# Created By  : David Arnold
# Created Date: 2019-11-21T11:08-05:00
# =============================================================================
"""This module implements a centralized monkey patcher for Odoo to suck less"""

__version__ = "0.0.1"
__all__ = ["monkeypatch", "Patcher"]

import logging
import re
from functools import partial, wraps

from psycopg2.extensions import make_dsn

_log = logging.getLogger(__name__)


# ==============
# Custom Errors
# ==============


class MokeyPatchError(RuntimeError):
    pass


# This solves quite a few design problems, use dodoo's cli tools
class DbOpsDisabledError(RuntimeError):
    pass


def monkeypatch(func):
    """ Decorator which identifies a method as a monkeypatch """

    @wraps(func)
    def decorated(*args, **kwargs):
        func(*args, **kwargs)

    decorated.monkeypatch = True
    return decorated


class Patcher:
    """A patcher class. Register additional patch methods decorating them with
    `@monkeypatch` from this module. They will be applied automatically after
    the general environment is built."""

    features = {}

    def __init__(self, odooconfig, dbconfig, smtpconfig):
        """Initializes the patcher and set's the feature flags"""
        self.OdooConfig = odooconfig
        self.DbConfig = dbconfig
        self.SmtpConfig = smtpconfig

    def patch(self):
        for isMonkeyPatch in self.__dict__.values():
            if hasattr(isMonkeyPatch, "monkeypatch"):
                try:
                    self[isMonkeyPatch]()
                except Exception:
                    msg = f"Patch {isMonkeyPatch} not applied"
                    _log.ciritcal(msg)
                    raise MokeyPatchError(msg)

    @monkeypatch
    def _patch_odoo_disable_db_ops(self):
        import odoo

        def alt(alternative, *args, **kwargs):
            raise DbOpsDisabledError(
                "Disabled for security reasons. "
                "Use '{alternative}' for this operation."
            )

        odoo.tools.misc.exec_pg_environ = partial(alt, "python code")
        odoo.tools.misc.exec_pg_command = partial(alt, "python code")
        odoo.tools.misc.exec_pg_command_pipe = partial(alt, "python code")
        odoo.tools.misc.find_pg_tool = partial(alt, "python code")
        odoo.service.db.exp_restore = partial(alt, "dodoo backup")
        odoo.service.db.exp_dump = partial(alt, "dodoo backup")
        odoo.service.db.exp_drop = partial(alt, "dodoo deinit")  # TODO: impl.

    @monkeypatch
    def _patch_odoo_verify_admin_password(self):
        import odoo

        def verify_admin_password(_self, password):
            return password == self.OdooConfig.Secrets.admin_passwd()

        odoo.tools.config.verify_admin_password = verify_admin_password

    @monkeypatch
    def _patch_odoo_connection_info_for(self):
        import odoo

        # Already reloaded by _patch_odoo_db_connect
        # reloaded = self.DbConfig.reload()

        def connection_info_for(dbname):
            dsn = self.DbConfig.resolve_dsn(dbname)
            return dbname, make_dsn(dsn, dbname=dbname)

        odoo.sql_db.connection_info_for = connection_info_for

    @monkeypatch
    def _patch_odoo_db_connect(self):
        import odoo

        reloaded = self.DbConfig.reload()
        if reloaded:  # We should recreate all connections
            odoo.sql_db.close_all()
        orig_method = odoo.sql_db.db_connect

        def db_connect(dbname):
            ConnectionPool = orig_method(dbname)
            maxconn = self.DbConfig.resolve_maxconn(dbname)
            ConnectionPool._maxconn = maxconn
            return ConnectionPool

        odoo.sql_db.db_connect = db_connect

    @monkeypatch
    def _patch_odoo_calling_home(self):
        if not self.features.get("call_home"):
            import odoo

            (
                odoo.addons.mail.models.update.PublisherWarrantyContract
            ).update_notification = lambda: True

    @monkeypatch
    def _patch_odoo_http_db_filter(self):
        import odoo

        def db_filter(dbs, httprequest=None):
            httprequest = httprequest or odoo.http.request.httprequest
            host = re.escape(httprequest.environ.get("HTTP_HOST", "").split(":")[0])
            version = re.escape(odoo.release.version)
            pattern = rf"{host}-{version}"
            if self.OdooConfig.list_db:
                pattern = rf".*-{version}"
            dbs = [i for i in dbs if re.match(pattern, i)]
            return dbs

    @monkeypatch
    def _patch_odoo_config(self):
        import odoo

        odoo.tools.config._parse_config()  # Generate default
        for k, v in self.OdooConfig.__dict__:
            odoo.tools.config[k] = v
        odoo.tools.config["list_db"] = self.OdooConfig.list_db
        addons_paths = self.OdooConfig.resolve_addons_paths()
        odoo.tools.config["addons_path"] = ",".join(
            addons_paths, odoo.tools.config["addons_path"].split(",")
        )
        odoo.conf.addons_paths = addons_paths + odoo.conf.addons_paths
        odoo.conf.server_wide_modules = list(self.OdooConfig.server_wide_modules)

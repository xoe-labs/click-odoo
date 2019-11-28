#!/usr/bin/env python3
# =============================================================================
# Created By  : David Arnold
# Created Date: 2019-11-21T11:08-05:00
# =============================================================================
"""This module implements a centralized monkey patcher for Odoo to suck less"""

__version__ = "0.0.1"
__all__ = ["monkeypatch", "Patcher"]

import logging
import os
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
    def _patch_odoo_ir_modules_install_from_url(self):
        """This essentially is a security patch as no rpc callable method
        should be allowed to mess with / inject server file system state.
        To enable this, you should write an explicit dodoo subcommand,
        this feature flag is not exposed nowhere for purpose."""

        # When I saw this first time, I was like: WTF?!?!?!
        # Side effects are somewhat frightning on a shared instance getting
        # into hands of knowledgeable people.

        if not self.features.get("install_remote_modules_via_rpc"):
            import odoo

            odoo.base.ir_modules.install_from_urls = lambda: True

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
    def _patch_odoo_module_get_modules(self):
        import odoo

        class CustomList(list):
            db_scoped = {}

        odoo.modules.module.ad_paths = CustomList([])

        def get_modules_with_version():
            """ Not used anywhere in standard odoo code, but might convey
            inacceptable side effects on the folllowing patch"""
            raise NotImplementedError(
                "Fail hard and early. Your code is not compatible with dodoo. "
                "This is a very, very rare case. Please refactor calls to "
                "`odoo.modules.module.get_modules_with_version()` "
                "while considering undesired side effects on dodoo's patched "
                "`odoo.modules.module.get_modules()`"
            )

        def get_modules():
            """Returns the list of module names eventually including
            database scoped modules
            """

            # ###################################################
            # Inspect caller for method-name based case branching
            # ###################################################
            import inspect

            frame = inspect.currentframe().f_back

            if frame.f_code.co_name == "update_list":
                # We are to update a database's module table
                # This is the magic: if not listed, the instance will not
                # be able to install a module.
                cr = frame.f_locals.get("self").env.cr
                cr.execute(
                    """
                    SELECT value FROM ir_config_parameter
                    WHERE key='database.uuid'
                """
                )
                return_db_scoped_paths = False
                (dbuuid,) = cr.fetchone()

            elif frame.f_code.co_name == "initialize":
                # We are first time initializing a database,
                # still, there is no dbuuid, so don't load any
                # custom modules
                # Note: we use dbuuid in order to not to produce side effects
                # for later db / host renaming operations done at higher levels
                # of infrastructure management in the case dbnames are filtered
                # by hostname. Therefore we need to forgo custom modules
                # at this stage, this is not a problem, as `update_list` is
                # called in sufficient occasions eventually satisfying an
                # updated database representation of the available modules.
                return_db_scoped_paths = False
                dbuuid = None

            else:
                # Just beahve as if all configured paths where be regarded.
                # It is ensured by construction, that add_paths also includes
                # the custom module paths.
                # On v12, this is called in one of:
                # odoo/addons/test_lint/tests/test_ecmascript.py: a test case
                #   for js code linting
                # odoo/addons/test_lint/tests/test_pylint.py: a test case for
                #   py code linting
                # odoo/cli/command.py: a hook for extending the odoo command -
                #   irrelevant in a dodoo context
                # odoo/service/server.py: used for logging server config
                #   parameters - we do it our way in dodoo
                return_db_scoped_paths = True
                dbuuid = None
            frame.clear()  # cleare references for GC (memory management)
            # ###########
            # End inspect
            # ###########

            if dbuuid:
                ad_paths = (
                    odoo.modules.module.ad_paths
                    - odoo.modules.module.ad_paths.db_scoped.values()
                    + odoo.modules.module.ad_paths.db_scoped.get(dbuuid, [])
                )
            elif not return_db_scoped_paths:
                ad_paths = (
                    odoo.modules.module.ad_paths
                    - odoo.modules.module.ad_paths.db_scoped.values()
                )
            else:
                ad_paths = odoo.modules.module.ad_paths

            def listdir(dir):
                def clean(name):
                    name = os.path.basename(name)
                    if name[-4:] == ".zip":
                        name = name[:-4]
                    return name

                def is_really_module(name):
                    for mname in odoo.modules.module.MANIFEST_NAMES:
                        if os.path.isfile(os.path.join(dir, name, mname)):
                            return True

                return [clean(it) for it in os.listdir(dir) if is_really_module(it)]

            plist = []
            odoo.modules.module.initialize_sys_path()
            for ad in ad_paths:
                plist.extend(listdir(ad))
            return list(set(plist))

        odoo.modules.get_modules_with_version = get_modules_with_version
        odoo.modules.module.get_modules_with_version = get_modules_with_version
        odoo.modules.get_modules = get_modules
        odoo.modules.module.get_modules = get_modules

    @monkeypatch
    def _patch_odoo_config(self):
        import odoo

        odoo.tools.config._parse_config()  # Generate default
        for k, v in self.OdooConfig.__dict__:
            odoo.tools.config[k] = v
        odoo.tools.config["list_db"] = self.OdooConfig.list_db
        scoped_addons = self.OdooConfig.resolve_scoped_addons_dir()
        addons_paths = (
            # Add scoped addons to the general addons path, they are filtered
            # in due occasions by patched `get_modules`
            scoped_addons.values()
            + self.OdooConfig.resolve_addons_paths()
        )
        odoo.tools.config["addons_path"] = ",".join(
            addons_paths, odoo.tools.config["addons_path"].split(",")
        )
        # Store them for significant reference used by patched `get_modules`
        # to unwrap and reason about the patched scope it should return; see
        # `CustomList` above
        odoo.modules.module.ad_paths.db_scoped = scoped_addons
        odoo.conf.addons_paths = addons_paths + odoo.conf.addons_paths
        odoo.conf.server_wide_modules = list(self.OdooConfig.server_wide_modules)

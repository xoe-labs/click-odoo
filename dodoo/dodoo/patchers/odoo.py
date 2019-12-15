# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements a centralized monkey patcher for Odoo to suck less"""


import logging
import os
import re
from functools import partial

from psycopg2.extensions import make_dsn, parse_dsn

import dodoo
from dodoo.interfaces import odoo
from dodoo.patchers import BasePatcher

_log = logging.getLogger(__name__)


# ==============
# Custom Errors
# ==============


# This solves quite a few design problems, use dodoo's cli tools
class DbOpsDisabledError(RuntimeError):
    pass


def _db_ops_alternative(alternative, *args, **kwargs):
    raise DbOpsDisabledError(
        "Disabled for security reasons. " "Use {alternative} for this operation."
    )


# Inheriting order important
class Patcher(odoo.Patchable, BasePatcher):
    def __init__(self, odooconfig, dbconfig, smtpconfig):
        """Initializes the patcher and set's the feature flags"""
        self.OdooConfig = odooconfig
        self.DbConfig = dbconfig
        self.SmtpConfig = smtpconfig

    @staticmethod
    def exec_pg_environ():
        return partial(_db_ops_alternative, "python code")

    @staticmethod
    def exec_pg_command():
        return partial(_db_ops_alternative, "python code")

    @staticmethod
    def exec_pg_command_pipe():
        return partial(_db_ops_alternative, "python code")

    @staticmethod
    def find_pg_tool():
        return partial(_db_ops_alternative, "python code")

    @staticmethod
    def exp_restore():
        return partial(_db_ops_alternative, "'dodoo backup")

    @staticmethod
    def exp_dump():
        return partial(_db_ops_alternative, "'dodoo backup'")

    @staticmethod
    def exp_drop():
        return partial(_db_ops_alternative, "'dodoo deinit'")  # TODO: impl.

    def verify_admin_password(self, _self, password):
        return password == self.OdooConfig.Sec.admin_passwd

    def connection_info_for(self, dbname):
        # Already reloaded by _patch_odoo_db_connect
        # reloaded = self.DbConfig.reload()
        dsn = self.DbConfig.resolve_dsn(dbname)
        return dbname, parse_dsn(make_dsn(dsn, dbname=dbname, application_name="odoo"))

    orig_db_connect = odoo.Patchable().db_connect

    def db_connect(self, dbname):
        reloaded = self.DbConfig.reload()
        if reloaded:  # We should recreate all connections
            odoo.Database().close_all()
        Connection = Patcher.orig_db_connect(dbname)
        # Todo: find a way to enable per-database connections
        # Connection._maxconn = self.DbConfig.resolve_maxconn(dbname)

        # As connections are pooled, the performance penalty is negligible
        with Connection.cursor() as cr:
            cr.execute(f"SET search_path TO odoo")
        return Connection

    @staticmethod
    @BasePatcher.unlessFeature("call_home")
    def update_notification():
        return lambda: True

    @staticmethod
    @BasePatcher.unlessFeature("install_remote_modules_via_rpc")
    def install_from_urls():
        return lambda: True

    def db_filter(self, dbs, httprequest=None):
        httprequest = httprequest or odoo.http.request.httprequest
        host = re.escape(httprequest.environ.get("HTTP_HOST", "").split(":")[0])
        project_version = re.escape(dodoo.framework().dodoo_project_version)
        pattern = rf"{host}-{project_version}"
        if self.OdooConfig.list_db:
            pattern = rf".*-{project_version}"
        dbs = [i for i in dbs if re.match(pattern, i)]
        return dbs

    @property
    def ad_paths(self):
        db_scoped = self.OdooConfig.resolve_scoped_addons_dir()

        class CustomList(list):
            pass

        # Store them for significant reference used by patched `get_modules`
        # to unwrap and reason about the patched scope it should return
        CustomList.db_scoped = db_scoped
        return CustomList([])

    @staticmethod
    def get_modules_with_version():
        """ Not used anywhere in standard odoo code, but conveys possible and
        inacceptable side effects on `get_modules` patch."""
        raise NotImplementedError(
            "Fail hard and early. Your code is not compatible with dodoo. "
            "This is a very, very rare case. Please refactor calls to "
            "`odoo.modules.module.get_modules_with_version()` "
            "while considering undesired side effects on dodoo's patched "
            "`odoo.modules.module.get_modules()`"
        )

    @staticmethod
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
            ad_paths = list(
                set(odoo.Patchable.ad_paths)
                - set(odoo.Patchable.ad_paths.db_scoped.values())
                | set(odoo.Patchable.ad_paths.db_scoped.get(dbuuid, []))
            )
        elif not return_db_scoped_paths:
            ad_paths = list(
                set(odoo.Patchable.ad_paths)
                - set(odoo.Patchable.ad_paths.db_scoped.values())
            )
        else:
            ad_paths = odoo.Patchable.ad_paths

        def listdir(dir):
            def clean(name):
                name = os.path.basename(name)
                if name[-4:] == ".zip":
                    name = name[:-4]
                return name

            def is_really_module(name):
                for mname in odoo.Modules().MANIFEST_NAMES:
                    if os.path.isfile(os.path.join(dir, name, mname)):
                        return True

            return [clean(it) for it in os.listdir(dir) if is_really_module(it)]

        plist = []
        odoo.Modules().initialize_sys_path()
        for ad in ad_paths:
            plist.extend(listdir(ad))
        return list(set(plist))

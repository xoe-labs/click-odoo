# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements an interface to the odoo namespace.
Hence, maintainers have a single source of truth of it's usage.
Consequent lazy loading of patchable properties ensures patchability.
For consistency, never access the odoo namespace directly."""

from importlib import import_module

from ..patchers import PatchableProperty as PProp


class Registry:
    pass


class Environment:
    pass


class Tools:
    @staticmethod
    def resetlocale():
        import_module("odoo.tools.translate.resetlocale")()


class Modules:
    @staticmethod
    def initialize_sys_path():
        import_module("odoo.modules.module.initialize_sys_path")()

    @property
    def MANIFEST_NAMES(self):
        return import_module("odoo.modules.module.MANIFEST_NAMES")

    @property
    def deduce_module_name_from(self, path):
        return import_module("odoo.modules.module.get_module_root")(path)


class Database:
    @staticmethod
    def close_all():
        import_module("odoo.sql_db.close_all")()


class Config:
    def __init__(self):
        self._config = None
        self._conf = None

    @property
    def config(self):
        if not self._config:
            self._config = import_module("odoo.tools.config")
        return self._config

    @property
    def conf(self):
        if not self._conf:
            self._conf = import_module("odoo.conf")
        return self._conf

    def defaults(self):
        self.config._parse_config()


class Patchable:

    # #############################
    # Index of patched namespaces #
    # #############################
    # odoo.addons.base
    # odoo.addons.mail
    # odoo.conf
    # odoo.http
    # odoo.modules.module
    # odoo.service.db
    # odoo.sql_db
    # odoo.tools.config
    # odoo.tools.misc
    # #############################

    # odoo.addons.base
    install_from_urls = PProp("odoo.addons.base.ir_modules.install_from_urls")

    # odoo.addons.mail
    update_notification = PProp(
        "odoo.addons.mail.models."
        "update.PublisherWarrantyContract.update_notification"
    )

    # odoo.http
    db_filter = PProp("odoo.http.db_filter")

    # odoo.modules.module
    ad_paths = PProp("odoo.modules.module.ad_paths")
    get_modules = PProp("odoo.modules.module.get_modules")
    get_modules_with_version = PProp("odoo.modules.module.get_modules_with_version")

    # odoo.service.db
    exp_drop = PProp("odoo.service.db.exp_drop")
    exp_dump = PProp("odoo.service.db.exp_dump")
    exp_restore = PProp("odoo.service.db.exp_restore")

    # odoo.sql_db
    connection_info_for = PProp("odoo.sql_db.connection_info_for")
    db_connect = PProp("odoo.sql_db.db_connect")

    # odoo.tools.config
    verify_admin_password = PProp("odoo.tools.config.verify_admin_password")

    # odoo.tools.misc
    exec_pg_command = PProp("odoo.tools.misc.exec_pg_command")
    exec_pg_command_pipe = PProp("odoo.tools.misc.exec_pg_command_pipe")
    exec_pg_environ = PProp("odoo.tools.misc.exec_pg_environ")
    find_pg_tool = PProp("odoo.tools.misc.find_pg_tool")

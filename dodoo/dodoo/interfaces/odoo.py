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


class Exceptions:
    def __init__(self):
        self._r = import_module("odoo.exceptions")

    @property
    def AccessDenied(self):
        return self._r.AccessDenied


class Authentication:
    @staticmethod
    def authenticate(database, login, password, context=None):
        if not context:
            context = {}
        common = import_module("odoo.service.common")
        return common.exp_authenticate(database, login, password, context)


class Logging:
    def __init__(self):
        self._r = import_module("odoo.netsvc")

    @property
    def ColoredPerfFilter(self):
        return self._r.ColoredPerfFilter

    @property
    def PerfFilter(self):
        return self._r.PerfFilter


class WSGI:
    def __init__(self):
        self._r = import_module("odoo.service.wsgi_server")

    @property
    def app(self):
        return self._r.application_unproxied


class Registry:
    def __new__(cls, dbname):
        registry = import_module("odoo.modules.registry")
        return registry.Registry(dbname)

    @staticmethod
    def items():
        registry = import_module("odoo.modules.registry")
        return registry.Registry.registries.items()


class Environment:
    def __new__(cls, cr, uid, context=None):
        if not context:
            context = {}
        Environment = import_module("odoo.api.Environment")
        with Environment.manage():
            yield Environment(cr, uid, context)


class Cron:
    def __init__(self):
        self._r = import_module("odoo.addons.base.models.ir_cron")

    def acquire(self, dbname):
        return self._r.ir_cron._acquire_job(dbname)


class Tools:
    def __init__(self):
        self._t = import_module("odoo.tools")
        self._f = import_module("odoo.tools.func")

    def resetlocale(self):
        self._t.resetlocale()

    def lazy(self, obj):
        return self._f.lazy(obj)


class Modules:
    def __init__(self):
        self._r = import_module("odoo.modules.module")

    def initialize_sys_path(self):
        self._r.initialize_sys_path()

    @property
    def MANIFEST_NAMES(self):
        return self._r.MANIFEST_NAMES

    @property
    def loaded(self):
        return self._r.loaded

    def load(self, module):
        return self._r.load_openerp_module(module)

    def deduce_module_name_from(self, path):
        return self._r.get_module_root(path)

    def deduce_module_and_relpath_from(self, path):
        res = self._r.get_resource_from_path(path)
        if not res:  # Fixing the return signature
            return None, None
        return res

    def parse_manifest_from(self, module):
        return self._r.load_information_from_description_file(module)


class Database:
    def __init__(self):
        self._r = import_module("odoo.sql_db")

    def close_all(self):
        self._r.close_all()


class Config:
    def __init__(self):
        self._config = None
        self._conf = None

    @property
    def config(self):
        if not self._config:
            self._config = import_module("odoo.tools.config").config
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
    install_from_urls = PProp(
        "odoo.addons.base.models.ir_module:Module.install_from_urls"
    )

    # odoo.addons.mail
    update_notification = PProp(
        "odoo.addons.mail.models."
        "update:PublisherWarrantyContract.update_notification"
    )

    # odoo.http
    db_filter = PProp("odoo.http:db_filter")

    # odoo.modules.module
    ad_paths = PProp("odoo.modules.module:ad_paths")
    get_modules = PProp("odoo.modules.module:get_modules")
    get_modules_with_version = PProp("odoo.modules.module:get_modules_with_version")

    # odoo.service.db
    exp_drop = PProp("odoo.service.db:exp_drop")
    exp_dump = PProp("odoo.service.db:exp_dump")
    exp_restore = PProp("odoo.service.db:exp_restore")

    # odoo.sql_db
    connection_info_for = PProp("odoo.sql_db:connection_info_for")
    db_connect = PProp("odoo.sql_db:db_connect")

    # odoo.tools.config
    verify_admin_password = PProp(
        "odoo.tools.config:configmanager.verify_admin_password"
    )

    # odoo.tools.misc
    exec_pg_command = PProp("odoo.tools.misc:exec_pg_command")
    exec_pg_command_pipe = PProp("odoo.tools.misc:exec_pg_command_pipe")
    exec_pg_environ = PProp("odoo.tools.misc:exec_pg_environ")
    find_pg_tool = PProp("odoo.tools.misc:find_pg_tool")

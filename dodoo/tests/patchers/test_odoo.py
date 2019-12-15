import logging

from dodoo import RUNMODE
from dodoo.configs import load_config
from dodoo.interfaces import odoo as odoo_interface
from dodoo.patchers.odoo import Patcher


class TestOdooPatcher:
    def test_apply(self, confd, caplog):
        caplog.set_level(logging.DEBUG)
        config = load_config(confd, RUNMODE.Production)
        Patcher(config.Odoo, config.Db, config.Smtp).apply()

        import odoo

        patcher_module = "dodoo.patchers.odoo"

        # Differences of __func__ accessor due to func vs method

        func = odoo.addons.base.models.ir_module.Module.install_from_urls
        assert odoo_interface.Patchable().install_from_urls is func
        assert func.__module__ == patcher_module

        func = (
            odoo.addons.mail.models.update.PublisherWarrantyContract.update_notification
        )
        assert odoo_interface.Patchable().update_notification is func
        assert func.__module__ == patcher_module

        func = odoo.http.db_filter
        assert odoo_interface.Patchable().db_filter is func
        assert func.__module__ == patcher_module

        customlist = odoo.modules.module.ad_paths
        assert odoo_interface.Patchable().ad_paths is customlist
        assert getattr(customlist, "db_scoped") == {}

        func = odoo.modules.module.get_modules
        assert odoo_interface.Patchable().get_modules is func
        assert func.__module__ == patcher_module

        func = odoo.modules.module.get_modules_with_version
        assert odoo_interface.Patchable().get_modules_with_version is func
        assert func.__module__ == patcher_module

        func = odoo.service.db.exp_drop
        assert odoo_interface.Patchable().exp_drop is func
        assert func.__module__ == patcher_module

        func = odoo.service.db.exp_dump
        assert odoo_interface.Patchable().exp_dump is func
        assert func.__module__ == patcher_module

        func = odoo.service.db.exp_restore
        assert odoo_interface.Patchable().exp_restore is func
        assert func.__module__ == patcher_module

        func = odoo.sql_db.connection_info_for
        assert odoo_interface.Patchable().connection_info_for is func
        assert func.__module__ == patcher_module

        func = odoo.sql_db.db_connect
        assert odoo_interface.Patchable().db_connect is func
        assert func.__module__ == patcher_module

        func = odoo.tools.config.verify_admin_password
        assert odoo_interface.Patchable().verify_admin_password is func
        assert func.__module__ == patcher_module

        func = odoo.tools.misc.exec_pg_command
        assert odoo_interface.Patchable().exec_pg_command is func
        assert func.__module__ == patcher_module

        func = odoo.tools.misc.exec_pg_command_pipe
        assert odoo_interface.Patchable().exec_pg_command_pipe is func
        assert func.__module__ == patcher_module

        func = odoo.tools.misc.exec_pg_environ
        assert odoo_interface.Patchable().exec_pg_environ is func
        assert func.__module__ == patcher_module

        func = odoo.tools.misc.find_pg_tool
        assert odoo_interface.Patchable().find_pg_tool is func
        assert func.__module__ == patcher_module

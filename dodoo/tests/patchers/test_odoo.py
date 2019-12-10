from dodoo import RUNMODE
from dodoo.configs import load_config
from dodoo.interfaces import odoo as odoo_interface
from dodoo.patchers.odoo import Patcher


class TestOdooPatcher:
    def test_apply(self, confd):
        config = load_config(confd, RUNMODE.Production)
        Patcher(config.Odoo, config.Db, config.Smtp).apply()

        import odoo

        assert odoo_interface.Patchable().db_filter == odoo.http.db_filter
        assert odoo.http.db_filter.__func__.__module__ == "dodoo.patchers.odoo"
        assert odoo.http.db_filter.__func__.__qualname__ == "Patcher.db_filter"

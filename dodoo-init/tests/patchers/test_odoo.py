from dodoo_init.interfaces import odoo as odoo_interface
from dodoo_init.patchers.odoo import AttachmentStoragePatcher


class TestOdooPatcher:
    def test_apply(self, main_loaded):
        AttachmentStoragePatcher().apply()
        import odoo

        correct_module = "dodoo_init.patchers.odoo"
        func = odoo.addons.base.models.ir_attachment.IrAttachment._storage
        assert odoo_interface.Patchable()._storage is func
        assert func.__func__.__module__ == correct_module

from dodoo_init.interfaces import odoo


class TestOdooInterface:
    def test_patchable(self):
        odoo.Patchable._storage

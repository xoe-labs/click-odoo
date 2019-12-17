odoo = odoo  # noqa
env = env  # noqa
self = self  # noqa

admin = env["res.users"].search([("login", "=", "admin")])
admin.login = "newadmin"

print(f"script - output: {odoo.release.version}:{self.id}:admin->{admin.login}")

odoo = odoo  # noqa
env = env  # noqa
self = self  # noqa

admin = env["res.users"].search([("login", "=", "admin")])
admin.login = "newadmin"

env.cr.commit()

print(f"script - output: {odoo.release.version}:{self.id}:admin->{admin.login}")

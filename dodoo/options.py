# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import click

from .env import odoo

# Default options
config_opt = click.option(
    "--config",
    "-c",
    envvar=["ODOO_RC", "OPENERP_SERVER"],
    type=click.Path(exists=True, dir_okay=True),
    help="Specify the Odoo configuration file. Other "
    "ways to provide it are with the ODOO_RC or "
    "OPENERP_SERVER environment variables, "
    "or ~/.odoorc (Odoo >= 10) "
    "or ~/.openerp_serverrc.",
)
log_level_opt = click.option(
    "--log-level",
    default=lambda: odoo.tools.config["log_level"],
    show_default=True,
    help="Specify the logging level. Accepted values depend "
    "on the Odoo version, and include debug, info, "
    "warn, error.",
)
logfile_opt = click.option(
    "--logfile",
    default=lambda: odoo.tools.config["logfile"],
    type=click.Path(dir_okay=False),
    help="Specify the log file.",
)


# Optional subcommand options
# Note: use of lambda makes them (potentially) configurable.
# Decorate with @options.an_option() instead of @options.an_option
def addons_path_opt(required=False):
    return click.option(
        "--addons-path",
        required=required,
        default=lambda: odoo.tools.config["addons_path"],
        envvar=["ODOO_ADDONS_PATH"],
        help="Specify the addons path. If present, this "
        "parameter takes precedence over the addons path "
        "provided in the Odoo configuration file.",
    )


def db_opt(required=False):
    return click.option(
        "--database",
        "-d",
        required=required,
        default=lambda: odoo.tools.config["db_name"],
        envvar=["PGDATABASE"],
        help="Specify the database name. If present, this "
        "parameter takes precedence over the database "
        "provided in the Odoo configuration file.",
    )


def rollback_opt():
    return click.option(
        "--rollback",
        is_flag=True,
        help="Rollback the transaction even if the script "
        "does not raise an exception. Note that if the "
        "script itself commits, this option has no effect. "
        "This is why it is not named dry run. This option "
        "is implied when an interactive console is "
        "started.",
    )

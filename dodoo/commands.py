#!/usr/bin/env python
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import sys
from contextlib import closing

import click

from . import options
from .env import OdooEnvironment, odoo

_logger = logging.getLogger(__name__)


def _db_exists(dbname):
    conn = odoo.sql_db.db_connect("postgres")
    with closing(conn.cursor()) as cr:
        cr._obj.execute(
            "SELECT datname FROM pg_catalog.pg_database "
            "WHERE lower(datname) = lower(%s)",
            (dbname,),
        )
        return bool(cr.fetchone())


class CommandWithOdooEnv(click.Command):
    def __init__(self, env_options=None, *args, **kwargs):
        env_options = env_options if env_options else {}
        super(CommandWithOdooEnv, self).__init__(*args, **kwargs)
        self.database = None
        self.rollback = None
        self.database_must_exist = env_options.get("database_must_exist", True)
        self.environment_manager = env_options.get(
            "environment_manager", OdooEnvironment
        )
        # Always present for an Odoo Environment
        options.config_opt(self)
        options.log_level_opt(self)
        options.logfile_opt(self)

    def _parse_env_args(self, ctx):
        def _get(flag):
            result = ctx.params.get(flag)
            if flag in ctx.params:
                del ctx.params[flag]
            return result

        odoo_args = []

        # fmt: off
        # Always present params
        config      = _get("config")       # noqa
        log_level   = _get("log_level")    # noqa
        logfile     = _get("logfile")      # noqa
        # Conditionally present params
        addons_path = _get("addons_path")  # noqa
        database    = _get("database")     # noqa
        rollback    = _get("rollback")     # noqa
        # fmt: on

        if config:
            odoo_args.extend(["-c", config])
        if log_level:
            odoo_args.extend(["--log-level", log_level])
        if logfile:
            odoo_args.extend(["--logfile", logfile])
        if addons_path:
            odoo_args.extend(["--addons-path", addons_path])
        if database:
            odoo_args.extend(["-d", database])
        if rollback:
            self.rollback = rollback
        return odoo_args

    def load_odoo_config(self, ctx):
        series = odoo.release.version_info[0]
        has_database_option = "database" in ctx.params

        def _fix_logging(series):
            if series < 9:
                handlers = logging.getLogger().handlers
                if handlers and len(handlers) == 1:
                    handler = handlers[0]
                    if isinstance(handler, logging.StreamHandler):
                        if handler.stream is sys.stdout:
                            handler.stream = sys.stderr

        odoo_args = self._parse_env_args(ctx)
        # see https://github.com/odoo/odoo/commit/b122217f74
        odoo.tools.config["load_language"] = None
        odoo.tools.config.parse_config(odoo_args)
        # Lookup from config file
        if has_database_option and not self.database:
            self.database = odoo.tools.config["db_name"]
        if self.database and self.database_must_exist and not _db_exists(self.database):
            raise click.UsageError(
                "The provided database does not exists and this script requires"
                " a pre-existing database."
            )
        elif self.database and not _db_exists(self.database):
            self.database = False
        _fix_logging(series)
        odoo.cli.server.report_configuration()

    def invoke(self, ctx):
        self.load_odoo_config(ctx)
        try:
            if self.database:
                with self.environment_manager(self) as env:
                    ctx.params["env"] = env
                    return super(CommandWithOdooEnv, self).invoke(ctx)
            else:
                with odoo.api.Environment.manage():
                    ctx.params["env"] = None
                    return super(CommandWithOdooEnv, self).invoke(ctx)
        except click.exceptions.Exit:
            raise
        except Exception as e:
            _logger.error("exception", exc_info=True)
            raise click.ClickException(str(e))

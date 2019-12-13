# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implments generic database utils with postgres in mind."""


from psycopg2.extensions import parse_dsn

import dodoo
from dodoo.connections import PublicCursor

from . import ensure_framework

# from `sh` will be lazily imported as it's no hard dependency of dodoo

MAINTENANCE_DATABASE = "postgres"


@ensure_framework
def _dsn_resolver(dbname):
    return dodoo.framework().dodoo_config.Db.resolve_dsn(dbname)


def _connection_args_from_dsn(dsn):
    params = parse_dsn(dsn)
    return [
        "-h",
        params["host"],
        "-U",
        params["user"],
        "-p",
        params["port"],
        "--no-password",
    ]


def maintenance_dsn():
    dsn = _dsn_resolver(MAINTENANCE_DATABASE)
    return dsn


def _maint_conn_args():
    dsn = _dsn_resolver(MAINTENANCE_DATABASE)
    args = _connection_args_from_dsn(dsn)
    return args


def drop_database(dbname):
    from sh import dropdb

    dropdb(*_maint_conn_args(), dbname)


def backup_database(dbname, file):
    from sh import pg_dump

    with file.open("wb") as f:
        pg_dump(*_maint_conn_args(), "--format=custom", dbname, _out=f)


def restore_database(dbname, file):
    from sh import pg_restore

    with file.open("rb") as f:
        pg_restore(*_maint_conn_args(), dbname, _in=f)


def copy_db(source, dest):
    from sh import createdb

    createdb(*_maint_conn_args(), "--locale=C", f"--template={source}", dest)


def db_exists(dbname):
    dsn = _dsn_resolver(MAINTENANCE_DATABASE)
    with PublicCursor(dsn) as cr:
        cr.execute(
            "SELECT datname FROM pg_catalog.pg_database "
            "WHERE lower(datname) = lower({%s});",
            (dbname,),
        )
        return bool(cr.fetchone())


def terminate_connections(dbname):
    dsn = _dsn_resolver(MAINTENANCE_DATABASE)
    with PublicCursor(dsn) as cr:
        cr.execute(
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = %s "
            "AND pid <> pg_backend_pid();",
            (dbname,),
        )
    return cr.rowcount

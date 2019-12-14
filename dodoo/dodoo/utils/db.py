# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implments generic database utils with postgres in mind."""

from pathlib import Path

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


def drop_database(dbname: str) -> None:
    from sh import dropdb

    dropdb(*_maint_conn_args(), dbname)


def backup_database(dbname: str, file: Path) -> None:
    from sh import pg_dump

    with file.open("wb") as file:
        pg_dump(*_maint_conn_args(), "--format=custom", dbname, _out=file)


def restore_database(dbname: str, file: Path) -> None:
    from sh import createdb

    createdb(
        *_maint_conn_args(),
        # see odoo/odoo 3edd504f17a2fe435ccd8235037e96c11ba96c18 for rational
        "--template=template0",
        "--encoding=unicode",
        "--locale=C",
        dbname,
    )

    from sh import pg_restore

    with file.open("rb") as file:
        pg_restore(*_maint_conn_args(), f"--dbname={dbname}", _in=file)


def copy_db(source: str, dest: str) -> None:
    from sh import createdb

    createdb(*_maint_conn_args(), f"--template={source}", dest)


def db_exists(dbname: str) -> None:
    dsn = _dsn_resolver(MAINTENANCE_DATABASE)
    with PublicCursor(dsn) as cr:
        cr.execute(
            "SELECT datname FROM pg_catalog.pg_database "
            "WHERE lower(datname) = lower(%s);",
            (dbname,),
        )
        return bool(cr.fetchone())


def terminate_connections(dbname: str) -> None:
    dsn = _dsn_resolver(MAINTENANCE_DATABASE)
    with PublicCursor(dsn) as cr:
        cr.execute(
            "SELECT count(pg_terminate_backend(pg_stat_activity.pid)) "
            "FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = %s "
            "AND pid <> pg_backend_pid();",
            (dbname,),
        )
    return cr.rowcount

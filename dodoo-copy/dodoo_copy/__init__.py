# =============================================================================
# Created By : David Arnold
# Credits    : Stéphane Bidoul, Thomas Binsfeld, Benjamin Willig
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo copy plugin"""

__version__ = "0.1.0"

import logging
import shutil
import dodoo
from dodoo.interfaces import odoo
from dodoo.connections import PublicCursor
from psycopg2.extensions import AsIs, quote_ident

_log = logging.getLogger(__name__)

MGT_DATABASE = "postgres"


def db_exists(cr, dbname):
    cr.execute(
        "SELECT datname FROM pg_catalog.pg_database "
        "WHERE lower(datname) = lower(%s)",
        (dbname,),
    )
    return bool(cr.fetchone())


def terminate_connections(cr, dbname):
    cr.execute(
        "SELECT pg_terminate_backend(pg_stat_activity.pid) "
        "FROM pg_stat_activity "
        "WHERE pg_stat_activity.datname = %s "
        "AND pid <> pg_backend_pid();",
        (dbname,),
    )
    return cr.rowcount


def _copy_db(cr, source, dest):
    cr.execute(
        "CREATE DATABASE %s WITH TEMPLATE %s",
        (AsIs(quote_ident(dest, cr)), AsIs(quote_ident(source, cr))),
    )


def _copy_filestore(source, dest):
    filestore_source = odoo.Config().filestore(source)
    if filestore_source.is_dir():
        filestore_dest = odoo.Config().filestore(dest)
        shutil.copytree(filestore_source, filestore_dest)


def copy(modules, force_disconnect, from_db, new_db):
    """ Create an Odoo database by copying an existing one.

    This script copies using postgres CREATEDB WITH TEMPLATE.
    It also copies the filestore.
    """
    dsn = dodoo.framework().dodoo_config.Db.resolve_dsn(MGT_DATABASE)
    with PublicCursor(dsn) as cr:
        if db_exists(cr, new_db):
            msg = f"Destination database {new_db} already exists."
            _log.error(msg)
            return
        if not db_exists(cr, from_db):
            msg = f"Source database {from_db} does not exist."
            _log.error(msg)
            return
        if force_disconnect:
            count = terminate_connections(from_db)
            if count:
                msg = (
                    f"Force disconnected {count} connections to source "
                    f"database {from_db}."
                )
                _log.warning(msg)
        _copy_db(cr, from_db, new_db)
    _copy_filestore(from_db, new_db)

    msg = f"Database and filestore copied from {from_db} to {new_db}."
    _log.info(msg)

    if not modules:
        odoo.Database().close_all()
        return

    odoo.Config().config["init"] = dict.fromkeys(modules, 1)
    odoo.Registry.update(new_db)
    odoo.Database().close_all()
    msg = f"Additional module(s) {','.join(modules)} installed."
    _log.info(msg)


if __name__ == "__main__":  # pragma: no cover
    copy()

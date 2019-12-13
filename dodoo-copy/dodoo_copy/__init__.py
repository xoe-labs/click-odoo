# =============================================================================
# Created By : David Arnold
# Credits    : Stéphane Bidoul, Thomas Binsfeld, Benjamin Willig
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo copy plugin"""

__version__ = "0.1.0"

import logging
from dodoo.interfaces import odoo
from dodoo.utils import odoo as odooutils
from dodoo.utils import ensure_framework
from dodoo.utils import db as dbutils

from typing import List

_log = logging.getLogger(__name__)


@ensure_framework
def install_modules(modules: List[str], dbname: str) -> None:
    odoo.Config().config["init"] = dict.fromkeys(modules, 1)
    odoo.Registry.update(dbname)
    odoo.Database().close_all()
    msg = f"Additional module(s) {','.join(modules)} installed."
    _log.info(msg)


def copy(modules: List[str], force_disconnect: bool, from_db: str, new_db: str) -> None:
    """ Create an Odoo database by copying an existing one.

    This script copies using postgres CREATEDB WITH TEMPLATE.
    It also copies the filestore.
    """
    new_exists = dbutils.db_exists(new_db)
    if new_exists:
        msg = f"Destination database {new_db} already exists."
        _log.error(msg)
        return
    from_exists = dbutils.db_exists(from_db)
    if not from_exists:
        msg = f"Source database {from_db} does not exist."
        _log.error(msg)
        return
    if force_disconnect:
        count = dbutils.terminate_connections(from_db)
        if count:
            msg = f"Disconnected {count} active connections from '{new_db}'."
            _log.warning(msg)
    dbutils.copy_db(from_db, new_db)
    odooutils.copy_filestore(from_db, new_db)

    msg = f"Database and filestore copied from {from_db} to {new_db}."
    _log.info(msg)

    if modules:
        install_modules(modules, new_db)


if __name__ == "__main__":  # pragma: no cover
    copy()

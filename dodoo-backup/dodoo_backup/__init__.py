# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo backup plugin"""

__version__ = "0.1.0"

import logging
import shutil
import tempfile

from dodoo.utils import odoo as odooutils
from dodoo.utils import db as dbutils

from contextlib import contextmanager

from datetime import datetime

from .file_type_identifier import file_type

from pathlib import Path

_log = logging.getLogger(__name__)


class FileNoteRecorgnized(Exception):
    pass


class FolderStructureUnkown(Exception):
    pass


@contextmanager
def _extracted(path: Path) -> Path:
    if path.is_dir():
        yield path
    ftype = file_type(str(path))
    if not ftype:
        raise FileNoteRecorgnized()
    with tempfile.TemporaryDirectory(prefix="extracted") as dir:
        dir = Path(str(dir))
        shutil.unpack_archive(path, dir, ftype)
        yield dir


def _validate_convention(dir: Path) -> bool:
    db_bkp = dir / "db.dump"
    if not db_bkp.is_file():
        raise FolderStructureUnkown()
    fs_bkp = dir / "filestore"
    if fs_bkp.exists() and not fs_bkp.is_dir():
        raise FolderStructureUnkown()
    return True


def backup(filestore_include: bool, dbname: str, dest: Path) -> Path:
    """Creates a compressed archive of an odoo instance backup, optionally
    with filestore included."""
    if not dbutils.db_exists(dbname):
        msg = f"Database {dbname} doesn't exists."
        _log.error(msg)
        return
    with tempfile.TemporaryDirectory(prefix="prepare") as dir:
        dir = Path(str(dir))
        # Convention!
        db_bkp = dir / "db.dump"
        fs_bkp = dir / "filestore"
        dbutils.backup_database(dbname, db_bkp)
        odooutils.backup_filestore(dbname, fs_bkp)
        timestamp = datetime.isoformat(datetime.now(), timespec="seconds")
        archive = dest / f"{timestamp}.{dbname}"
        archive = shutil.make_archive(archive, "gztar", dir)
        return Path(archive)


def restore(clear: bool, dbname: str, src: Path) -> None:
    """Restores an odoo instance backup, from one of the supported archives
    types: zip, tar, gztar, xztar, bztar."""

    exists = dbutils.db_exists(dbname)
    if exists and not clear:
        msg = f"Database {dbname} already exists."
        _log.error(msg)
        return

    with _extracted(src) as src:
        _validate_convention(src)
        # Keep this here after validation
        if exists:
            msg = f"Dropping database & filestore of {dbname} before restoring."
            _log.warning(msg)
            try:
                count = dbutils.terminate_connections(dbname)
                if count:
                    msg = f"Disconnected {count} active connections from '{dbname}'."
                    _log.warning(msg)
                dbutils.drop_database(dbname)
                odooutils.drop_filestore(dbname)
            except Exception:
                msg = f"Database & filestore fof {dbname} could not be pruned."
                _log.error(msg, exc_info=True)
                return
            else:
                msg = f"Database & filestore {dbname} pruned."
                _log.info(msg)
        # Convention!
        db_bkp = src / "db.dump"
        fs_bkp = src / "filestore"
        dbutils.restore_database(dbname, db_bkp)
        odooutils.restore_filestore(dbname, fs_bkp)
        msg = f"Database & filestore {dbname} restored."
        _log.info(msg)

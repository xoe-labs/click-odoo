# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo init plugin"""

__version__ = "0.1.0"

import csv
import hashlib
import logging
import os
from datetime import timedelta
from pathlib import Path
from dodoo.utils import odoo as odooutils
from dodoo.utils import db as dbutils
from dodoo.utils import ensure_framework
from dodoo.interfaces import odoo

from typing import List, Tuple

from .patchers.odoo import AttachmentStoragePatcher

from .cache import DbCache

_log = logging.getLogger(__name__)


EXCLUDE_PATTERNS = ("*.pyc", "*.pyo")
CACHE_PREFIX = "cache"


@ensure_framework
def odoo_createdb(dbname: str, with_demo: bool, modules: List[str]):
    """ Create an odoo database and initialize modules. Keep initial attachments
    within the database for cached template consistency."""
    odoo.Service().seed_db(dbname)
    odoo.Config().config["init"] = dict.fromkeys(modules, 1)
    odoo.Registry.update(dbname)

    msg = f"New database '{dbname}' created."
    _log.info(msg)

    if not with_demo:
        odoo.Database().close_all()
        return

    odoo.Modules().install_demo(dbname)
    msg = f"Demo data in '{dbname}' loaded."
    _log.info(msg)
    odoo.Database().close_all()


def _walk(top: str, exclude_patterns: Tuple[str] = EXCLUDE_PATTERNS) -> Path:
    """ Visit all files excluding specified patterns."""
    for root, dirnames, filenames in os.walk(top):
        root = Path(root)
        reltop = root.relative_to(top)
        dirnames.sort()
        for fname in sorted(filenames):
            fpath = reltop / fname
            for exclude_pattern in exclude_patterns:
                if not fpath.match(exclude_pattern):
                    yield fpath


def addons_digest(modules: List[str], with_demo: bool) -> bytes:
    """ Calculate digest of the source files of installable modules.
    Differenciate between demo and non-demo initializations."""
    h = hashlib.sha1()
    h.update(f"!demo={with_demo:d}!")
    for module in odooutils.expand_dependencies(modules):
        h.update(module.encode())
        module_path = odoo.Modules().module_path_from(module)
        for fpath in _walk(module_path):
            h.update(str(fpath).encode())
            h.update(fpath.read_bytes())
    return h.hexdigest()


def init(modules: List[str], with_demo: bool, no_cache: bool, database: str) -> None:
    """ Create an Odoo database with pre-installed modules.

    This script manages a cache of database templates with the exact same
    addons installed.

    Cache Keys:
        Templates are identified by computing a sha1 checksum over a file walk
        of the provided modules including their dependencies and corresponding
        auto installed modules.
    """

    # See commit 68f14c68709bbb50cb7fb66d288955e1d769c5ff in odoo/odoo
    csv.field_size_limit(500 * 1024 * 1024)

    if no_cache:
        odoo_createdb(database, with_demo, modules)

    digest = addons_digest(modules, with_demo)
    dsn = dbutils.maintenance_dsn()
    with DbCache(dsn, CACHE_PREFIX) as dbcache:
        created = dbcache.create(database, digest)
        if created:
            odoo.Modules().reflect(database)
            msg = f"New database '{database}' created from db cache."
            _log.info(msg)
        else:
            AttachmentStoragePatcher.apply()
            odoo_createdb(database, with_demo, modules)
            dbcache.add(database, digest)
            msg = f"Database '{database}' put in db cache."
            _log.info(msg)


def trim_cache(max_age: int, max_size: int) -> None:
    """ Trim the odoo database cache.
    """
    dsn = dbutils.maintenance_dsn()
    with DbCache(dsn, CACHE_PREFIX) as dbcache:
        if max_size:
            count = dbcache.trim_size(max_size)
            if count:
                msg = f"{count} database(s) cleared from cache (max-size)."
            else:
                msg = f"No database cleared from cache (max-size)."
            _log.info(msg)
        if max_age:
            count = dbcache.trim_age(timedelta(days=max_age))
            if count:
                msg = f"{count} database(s) cleared from cache (max-age)."
            else:
                msg = f"No database cleared from cache (max-age)."
            _log.info(msg)

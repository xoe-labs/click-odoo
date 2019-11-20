#!/usr/bin/env python3
# =============================================================================
# Created By  : David Arnold
# Created Date: 2019-11-20T11:08-05:00
# Credits     : Stéphane Bidoul, Thomas Binsfeld, Benjamin Willig
# License     : See github.com/xoe-labs/doDoo
# Status      : Development
# =============================================================================
"""This module implements the dodoo init subcommand, see readme for details"""

__version__ = "0.0.1"

import contextlib
import csv
import hashlib
import logging
import os
import re
from datetime import timedelta
from fnmatch import fnmatch

import click
import dodoo
from dodoo import odoo

from .cache import DbCache

_log = logging.getLogger(__name__)


EXCLUDE_PATTERNS = ("*.pyc", "*.pyo")
CACHE_PREFIX_REGEX = r"^[A-Za-z][A-Za-z0-9-]{0,7}$"

# ===================
# Compatibility Shims
# ===================


def IrAttachmentShim():  # noqa
    if odoo.release.version_info[0] >= 12:
        from odoo.addons.base.models.ir_attachment import IrAttachment
    elif odoo.release.version_info[0] >= 10:
        from odoo.addons.base.ir.ir_attachment import IrAttachment
    else:
        raise NotImplementedError("Versions prior 10 are not supported.")
    return IrAttachment


# ===================
# Mod. Implementation
# ===================


@contextlib.contextmanager
def _patch_ir_attachment_store():
    """ Make sure attachments created during db initialization are stored in
    database, so we get something consistent when recreating the db by copying
    the cached template."""
    IrAttachment = IrAttachmentShim()
    orig = IrAttachment._storage
    IrAttachment._storage = lambda: "db"
    try:
        yield
    finally:
        IrAttachment._storage = orig


def odoo_createdb(dbname, with_demo, module_names):
    """ Create an odoo database and initialize modules. Keep initial attachments
    within the database for cached template consistency."""
    with _patch_ir_attachment_store():
        odoo.service.db._create_empty_database(dbname)
        dodoo.config["init"] = dict.fromkeys(module_names, 1)
        dodoo.config["without_demo"] = not with_demo
        with dodoo.registry(dbname, force_demo=with_demo, update_module=True):
            msg = click.style(f"Created new Odoo database {dbname}.", fg="green")
            _log.info(msg)


def _walk(top, exclude_patterns=EXCLUDE_PATTERNS):
    """ Visit all files excluding specified patterns."""
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames.sort()
        reldir = os.path.relpath(dirpath, top)
        if reldir == ".":
            reldir = ""
        for filename in sorted(filenames):
            filepath = os.path.join(reldir, filename)
            for pattern in exclude_patterns:
                if fnmatch(filename, pattern):
                    continue
            yield filepath


def addons_digest(module_names, with_demo):
    """ Calculate digest of the source files of installable modules.
    Differenciate between demo and non-demo initializations."""
    h = hashlib.sha1()
    h.update(f"!demo={with_demo:d}!")
    full_module_list = sorted(dodoo.modules.expand(module_names, True, True))
    for module_name in full_module_list:
        module_path = dodoo.modules.path(module_name)
        h.update(module_name.encode())
        for filepath in _walk(module_path):
            h.update(filepath.encode())
            with open(os.path.join(module_path, filepath), "rb") as f:
                h.update(f.read())
    return h.hexdigest()


# ===================
# CLI Implementation
# ===================


# @click.command(cls=dodoo.CommandWithOdooEnv)
# @dodoo.options.addons_path_opt(True)
# @click.option(
#     "--new-database",
#     "-n",
#     required=False,
#     help="Name of new database to create, possibly from cache. "
#     "If absent, only the cache trimming operation is executed.",
# )
@click.option(
    "--install-modules",
    "-i",
    default="base",
    show_default=True,
    help="Comma separated list of addons to install.",
)
@click.option("--with-demo", flag=True, help="Load Odoo demo data.")
@click.option("--no-cache", flag=True, help="Don't use cache.")
@click.option(
    "--cache-prefix",
    default="cache",
    show_default=True,
    help="Cache prefix. Caution: identifies clearble artefacts",
)
@click.option(
    "--cache-max-age",
    default=30,
    show_default=True,
    type=int,
    help="Clear cache after so many days of non-usage." "Use -1 to disable.",
)
@click.option(
    "--cache-max-size",
    default=5,
    show_default=True,
    type=int,
    help="Keep N most recently used cache templates. Use "
    "-1 to disable. Use 0 to empty.",
)
@click.argument("database")
@click.argument("rawsql", required=False)
def init(
    env,
    install_modules,
    with_demo,
    no_cache,
    cache_prefix,
    cache_max_age,
    cache_max_size,
    database,
    rawsql,
):
    """ Create an Odoo database with pre-installed modules and seed it with SQL.

    This script manages a cache of database templates with the exact same
    addons installed.

    Raw SQL is executed after database creation and does not enter the cache.

    Cache Keys:
        Templates are identified by computing a sha1 checksum over a file walk
        of the provided modules including their dependencies and corresponding
        auto installed modules.

    Cache Prefix:
        Must comply with r"^[A-Za-z][A-Za-z0-9-]{0,7}$";
        notably have at most 8 characters.
    """

    # See commit 68f14c68709bbb50cb7fb66d288955e1d769c5ff in odoo/odoo
    csv.field_size_limit(500 * 1024 * 1024)

    module_names = [m.strip() for m in install_modules.split(",")]

    if no_cache:
        odoo_createdb(database, with_demo, module_names, False)
    elif re.match(CACHE_PREFIX_REGEX, cache_prefix):
        with DbCache(cache_prefix) as dbcache:
            digest = addons_digest(module_names, with_demo)
            created = dbcache.create(database, digest)
            if created:
                msg = click.style(
                    "Found matching database template.", fg="green", bold=True
                )
                _log.info(msg)
                dodoo.modules.reflect(database)
            else:
                odoo_createdb(database, with_demo, module_names)
                dbcache.add(database, digest)
                msg = click.style(
                    "New database created and cached.", fg="green", bold=True
                )
                _log.info(msg)
            if cache_max_size >= 0:
                dbcache.trim_size(cache_max_size)
            if cache_max_age >= 0:
                dbcache.trim_age(timedelta(days=cache_max_age))
    else:
        raise click.ClickException(
            f"Invalid cache prefix '{cache_prefix}', "
            f"validated against {CACHE_PREFIX_REGEX}."
        )

    if rawsql:
        with dodoo.oconn(database) as cr:
            cr.execute(rawsql)
            msg = click.style("Raw SQL loaded.", fg="green", bold=True)
            _log.info(msg)


if __name__ == "__main__":  # pragma: no cover
    init()

# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the odoo configuration"""


import logging
import os
import pathlib  # for monkey patches
from pathlib import Path
from typing import FrozenSet, List

from dataclasses import InitVar, dataclass, field
from dodoo.interfaces import odoo

from . import BaseConfig, PathLike, read_secret
from ._errors import NoPathError, PathNoDirError, PathNoFileError, PathNotAbsoluteError

_log = logging.getLogger(__name__)


pathlib.Path._serialize = PathLike._serialize
pathlib.PosixPath._serialize = PathLike._serialize


def find_addons_path(addons_dir: os.PathLike):
    """Recursively find all addons path within a directory"""
    paths = set()
    for root, dirnames, files in os.walk(addons_dir):
        if Path(root).parent in paths:
            dirnames.clear()
            continue
        if "__init__.py" in files:
            dirnames.clear()
        if not any(M in files for M in odoo.Modules().MANIFEST_NAMES):
            continue
        paths |= {Path(root).parent}
    return sorted(list(paths))  # We promise alphabetical order


def find_scoped_addons_path(addons_dir: os.PathLike):
    """Find all addons path within a directory, the first level
    sub-directories beeing expected to be DBUUIDs."""
    paths_map = {}
    for dbuuid in addons_dir.iterdir():
        if not dbuuid.is_dir():
            continue
        paths_map[dbuuid] = find_addons_path(dbuuid)
    return paths_map


@dataclass(frozen=True)
class OdooConfig(BaseConfig):

    validate: InitVar[bool] = True

    list_db = False  # Immutable
    # fmt: off
    data_dir:             PathLike = Path("/mnt/odoo/persist")  # noqa: E241
    backup_dir:           PathLike = Path("/mnt/odoo/backup")  # noqa: E241
    addons_dir:           PathLike = Path("/mnt/odoo/addons")  # noqa: E241
    scoped_addons_dir:    PathLike = Path("/mnt/odoo/scoped_addons")  # noqa: E241
    geoip_database:       PathLike = Path("/usr/share/GeoIP/GeoLite2-City.mmdb")  # noqa: E241
    unaccent:                 bool = True  # noqa: E241
    server_wide_modules: FrozenSet[str] = frozenset(["web", "base"])  # noqa: E241
    log_handler:         FrozenSet[str] = frozenset(["odoo.http.rpc.request:INFO",  # noqa: E241
                                                "odoo.http.rpc.response:INFO", ])

    # Secrets
    class Sec():
        __slots__ = []  # Immutable

        @property
        def admin_passwd(self):
            return read_secret("ODOOADMINPASSWORD_FILE")

        @property
        def session_encryption_key(self):
            return read_secret("SESSION_ENCRYPTION_KEY_FILE")

    Sec = Sec()
    # fmt: on

    def apply_log_handler_to(self, logging):
        for element in self.log_handler:
            loggername, level = element.split(":")
            level = getattr(logging, level, logging.INFO)
            logger = logging.getLogger(loggername)
            logger.setLevel(level)
            _log.debug(f"logger level set: {element}")

    def apply(self):
        cfg = odoo.Config()
        for k, v in self.__dict__.items():
            cfg.config[k] = v
        cfg.config["list_db"] = self.list_db
        cfg.config["addons_path"] = ",".join(
            [str(self.scoped_addons_dir)]
            + [str(p) for p in self.resolve_addons_paths()]
            + cfg.config["addons_path"].split(",")
        )
        # Fix frozenset config value
        cfg.config["server_wide_modules"] = ",".join(cfg.config["server_wide_modules"])
        cfg.config["log_handler"] = ",".join(cfg.config["log_handler"])
        # Fix Path objects
        cfg.config["data_dir"] = str(cfg.config["data_dir"])
        cfg.config["backup_dir"] = str(cfg.config["backup_dir"])
        cfg.config["geoip_database"] = str(cfg.config["geoip_database"])
        # Fix loaded defaults
        cfg.conf.addons_paths = cfg.config["addons_path"].split(",")
        server_wide_modules = cfg.config["server_wide_modules"].split(",")
        cfg.conf.server_wide_modules = [
            m.strip() for m in server_wide_modules if m.strip()
        ]

    def resolve_addons_paths(self):
        return find_addons_path(self.addons_dir)

    def resolve_scoped_addons_dir(self):
        return find_scoped_addons_path(self.scoped_addons_dir)

    def _validate(self):
        """Validate values against additional constraints"""
        super()._validate()

        def _exists_and_absolute(path):
            if not path.exists():
                raise NoPathError(path)
            if not path.is_absolute():
                raise PathNotAbsoluteError(path)

        def _is_dir(path):
            if not path.is_dir():
                raise PathNoDirError(path)

        def _is_file(path):
            if not path.is_file():
                raise PathNoFileError(path)

        _exists_and_absolute(self.data_dir)
        _exists_and_absolute(self.backup_dir)
        _exists_and_absolute(self.addons_dir)
        _exists_and_absolute(self.scoped_addons_dir)
        _exists_and_absolute(self.geoip_database)
        _is_dir(self.data_dir)
        _is_dir(self.backup_dir)
        _is_dir(self.addons_dir)
        _is_dir(self.scoped_addons_dir)
        _is_file(self.geoip_database)


@dataclass(frozen=True)
class OdooConfigProd(OdooConfig):
    _file_name = "odooconfig.prod.json"


@dataclass(frozen=True)
class OdooConfigStage(OdooConfigProd):
    _file_name = "odooconfig.stage.json"
    list_db: bool = True


# py38 syntax: Literal
# DevFlags = List[
#   Optional[Literal['pudb', 'wdb', 'ipdb', 'pdb']],
#   Optional[Literal['reload']],
#   Optional[Literal['qweb']],
#   Optional[Literal['werkzeug']],
#   Optional[Literal['xml']]
# ]
DevFlags = List[str]


@dataclass(frozen=True)
class OdooConfigDevelop(OdooConfigProd):
    _file_name = "odooconfig.develop.json"
    _dev_mode = lambda: ["pdb", "reload", "qweb", "xml"]  # noqa: E731
    list_db: bool = True
    dev_mode: DevFlags = field(default_factory=_dev_mode)
    # Create with https://github.com/FiloSottile/mkcert
    ssl_keyfile: PathLike = None
    ssl_certfile: PathLike = None

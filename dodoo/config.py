#!/usr/bin/env python3
# =============================================================================
# Created By  : David Arnold
# Created Date: 2019-11-20T11:08-05:00
# =============================================================================
"""This module implements the dodoo.config api for Odoo server configuration"""


__version__ = "0.0.1"
__all__ = ["OdooConfig", "DbConfig", "SmtpConfig"]


import json
import logging
import os
import re
import stat
from pathlib import Path
from typing import List

from psycopg2.extensions import make_dsn, parse_dsn

from dataclasses import dataclass, field

from .modules import find_addons_path

_log = logging.getLogger(__name__)

DEFAULT_ODOOADMINPASSWORD_FILE: str = "/run/secrets/adminpasswd"
DEFAULT_PGPASS_FILE: str = "/run/secrets/pgpass"
DEFAULT_SMTPUSER_FILE: str = "/run/secrets/smtpuser"
DEFAULT_SMTPPASSWORD_FILE: str = "/run/secrets/smtppassword"

# ==============
# Custom Errors
# ==============


class ConfigError(RuntimeError):
    pass


class ConfigDirNoDirError(ConfigError):
    pass


class NoConfigDirError(ConfigError):
    pass


class ConfigDirOwnershipError(ConfigError):
    pass


class InvalidOptionError(ConfigError):
    pass


class InvalidOptionTypeError(InvalidOptionError):
    pass


class SecretError(ConfigError):
    pass


class NoSecretError(SecretError):
    pass


class SecretNoFileError(SecretError):
    pass


class SecretOwnershipError(SecretError):
    pass


class PathError(ConfigError):
    pass


class NoPathError(PathError):
    pass


class PathNoDirError(PathError):
    pass


class PathNoFileError(PathError):
    pass


class PathNotAbsoluteError(PathError):
    pass


class NoSecretsInConfigError(ConfigError):
    pass


# ==============
# SecOps
# ==============


def _read_secret(env_var: str) -> str:
    path = Path(os.environ.get(env_var, globals().get("DEFAULT_" + env_var)))
    # Check when accessed to enforce restrictive config api
    if not path.is_absolute():
        raise PathNotAbsoluteError(path)
    if not path.exists():
        raise NoSecretError(path)
    if not path.is_file():
        raise SecretNoFileError(path)
    if stat.S_IMODE(path.lstat().st_mode) > 0o400:
        oct_str = oct(stat.S_IMODE(path.lstat().st_mode))
        raise SecretOwnershipError(
            f"{path} ownership is {oct_str}, max allowed is `0o400`"
        )
    return path.read_text().rstrip()


# ==============
# Config Impl.
# ==============


def _validate_confd(confd: os.PathLike) -> None:
    if not confd.exists():
        raise NoConfigDirError(f"{confd} does not exist.")
    if not confd.is_dir():
        raise ConfigDirNoDirError(f"{confd} is not a directory.")
    if stat.S_IMODE(confd.lstat().st_mode) > 0o440:
        oct_str = oct(stat.S_IMODE(confd.lstat().st_mode))
        raise ConfigDirOwnershipError(
            f"{confd} ownership is {oct_str}, max allowed is `0o440`"
        )
    for child in confd.iterdir():
        if not child.is_file():
            _log.warning(f"Config dir '{confd}' only contains files, not '{child}'!")
        if child.suffix != "*.json":
            _log.warning(
                f"Config dir '{confd}' only contains json files, not '{child.name}'!"
            )


class _Config:
    @classmethod
    def __new__(cls, confd: os.PathLike):
        _validate_confd(confd)
        cls.confd = confd
        cfg = {}
        for child in cls.confd.iterdir():
            if child.name == cls._file_name:
                cfg = json.load(child)
                cls._cast(cfg)
                cls._cure(cfg)
                break
        try:
            return super().__new__(cls, **cfg)
        except TypeError as e:
            raise InvalidOptionError(e.args[0])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validate()

    def reload(self):
        try:
            newconfig = self.__class__(self.confd)
            if self != newconfig:
                _log.info(f"Updated {self.__name__}.")
                self = newconfig
                return True
            else:
                return False
        except Exception:
            _log.warning(f"Hot reload of {self.__name__} failed.")
            return False

    @staticmethod
    def _cast(cfg: dict):
        return

    @staticmethod
    def _cure(cfg: dict):
        return

    def _validate(self):
        for k, v in self.__dict__:
            orig_type = self.__dataklass_fields[k].type
            if orig_type == v.type:
                continue
            msg = (
                f"Type '{v.type.__qualname__}' does not "
                f"conform to '{orig_type.__qualname__}'"
            )
            InvalidOptionTypeError(msg)
        return


# ==============
# Odoo Config
# ==============


@dataclass(frozen=True)
class OdooConfig(_Config):
    list_db = False  # Immutable
    # fmt: off
    data_dir:          os.PathLike = Path("/mnt/odoo/persist")  # noqa: E241
    backup_dir:        os.PathLike = Path("/mnt/odoo/backup")  # noqa: E241
    addons_dir:        os.PathLike = Path("/mnt/odoo/addons")   # noqa: E241
    geoip_database:    os.PathLike = Path("/usr/share/GeoIP/GeoLite2-City.mmdb")  # noqa: E241
    unaccent:                 bool = True  # noqa: E241
    server_wide_modules: frozenset = frozenset(["web", "base"])  # noqa: E241
    log_handler:         frozenset = frozenset(["odoo.http.rpc.request:INFO",  # noqa: E241
                                                "odoo.http.rpc.response:INFO", ])

    # Secrets
    class Sec():
        __slots__ = []  # Immutable
        admin_passwd = lambda: _read_secret("ODOOADMINPASSWORD_FILE")  # noqa: E731
    Sec = Sec()
    # fmt: on

    def apply_log_handler_to(self, logging):
        for element in self.log_handler:
            loggername, level = element.split(":")
            level = getattr(logging, level, logging.INFO)
            logger = logging.getLogger(loggername)
            logger.setLevel(level)
            _log.debug('logger level set: "%s"', element)

    def resolve_addons_paths(self):
        return find_addons_path(self.addons_dir)

    @staticmethod
    def _cast(cfg: dict):
        """Cast values from dictionary to this object's expected type"""
        if cfg.get("dbfilter"):
            cfg["dbfilter"] = re.compile(cfg.get("dbfilter"))
        if cfg.get("data_dir"):
            cfg["data_dir"] = Path(cfg.get("data_dir"))
        if cfg.get("backup_dir"):
            cfg["backup_dir"] = Path(cfg.get("backup_dir"))
        if cfg.get("addons_dir"):
            cfg["addons_dir"] = Path(cfg.get("addons_dir"))
        if cfg.get("geoip_database"):
            cfg["geoip_database"] = Path(cfg.get("geoip_database"))

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
        _exists_and_absolute(self.geoip_database)
        _is_dir(self.data_dir)
        _is_dir(self.backup_dir)
        _is_dir(self.addons_dir)
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
    _dev_mode = lambda: ["ipdb", "reload", "qweb", "xml"]  # noqa: E731
    list_db: bool = True
    dev_mode: DevFlags = field(default_factory=_dev_mode)


# ==============
# Db Config
# ==============

passfile = Path(os.environ.get("PGPASS_FILE", globals().get("DEFAULT_PGPASS_FILE")))


@dataclass(frozen=True)
class DbConfig(_Config):
    _default_dsn = f"user=odoo host=db port=5432 passfile={passfile}"
    # fmt: off
    default_maxconn:     int = 64  # noqa: E241
    default_dsn:         str = _default_dsn  # noqa: E241
    per_dbname_dsn:     dict = field(default_factory=dict)  # noqa: E241
    per_dbname_maxconn: dict = field(default_factory=dict)  # noqa: E241
    # fmt: on

    def resolve_dsn(self, dbname):
        if self.per_dbname_dsn.get(dbname):
            return self.per_dbname_dsn.get(dbname)
        return self.default_dsn

    def resolve_maxconn(self, dbname):
        if self.per_dbname_maxconn.get(dbname):
            return self.per_dbname_maxconn.get(dbname)
        return self.default_maxconn

    @staticmethod
    def _cure(cfg: dict):
        """Ensure dsn contains passfile"""

        def _ensure_dsn_with_passfile(dsn):
            dsn_dict = parse_dsn(dsn)  # Validates here as (desireable) side effect
            if not dsn_dict.get("passfile"):
                dsn_dict["passfile"] = passfile
            return make_dsn(dsn_dict)

        if cfg.get("default_dsn"):
            cfg["default_dsn"] = _ensure_dsn_with_passfile(cfg.get("default_dsn"))
        if cfg.get("per_dbname_dsn"):
            for dbname, dsn in cfg.get("per_dbname_dsn"):
                cfg["per_dbname_dsn"][dbname] = _ensure_dsn_with_passfile(dsn)

    def _validate(self):
        """Validate values against additional constraints"""
        super()._validate()

        def _contains_no_password(dsn):
            if "password" in dsn:
                raise NoSecretsInConfigError(dsn)

        _contains_no_password(self.default_dsn)
        for _dbname, dsn in self.per_dbname_dsn:
            _contains_no_password(dsn)


@dataclass(frozen=True)
class DbConfigProd(DbConfig):
    _file_name = "dbconfig.prod.json"


@dataclass(frozen=True)
class DbConfigStage(DbConfigProd):
    _file_name = "dbconfig.stage.json"
    default_maxconn: int = 1  # noqa: E241


@dataclass(frozen=True)
class DbConfigDevelop(DbConfigProd):
    _file_name = "dbconfig.develop.json"
    default_maxconn: int = 3  # noqa: E241


# ==============
# Smtp Config
# ==============


@dataclass(frozen=True)
class SmtpConfig(_Config):
    # fmt: off
    email_from:   bool = False  # noqa: E241
    server:       bool = False  # noqa: E241
    port:          int = 25  # noqa: E241
    ssl:          bool = True  # noqa: E241

    # Secrets
    class Sec():
        __slots__ = []  # Immutable
        user = lambda self: _read_secret("SMTPUSER_FILE")  # noqa: E731
        password = lambda self: _read_secret("SMTPPASSWORD_FILE")  # noqa: E731
    Sec = Sec()
    # fmt: on


@dataclass(frozen=True)
class SmtpConfigProd(SmtpConfig):
    _file_name = "smtpconfig.prod.json"


@dataclass(frozen=True)
class SmtpConfigStage(SmtpConfigProd):
    _file_name = "smtpconfig.stage.json"


@dataclass(frozen=True)
class SmtpConfigDevelop(SmtpConfigProd):
    _file_name = "smtpconfig.develop.json"
    ssl: bool = False  # noqa: E241

#!/usr/bin/env python3
# =============================================================================
# Created By  : David Arnold
# Created Date: 2019-11-20T11:08-05:00
# =============================================================================
"""This module implements the dodoo.config api for Odoo server configuration"""


__version__ = "0.0.1"
__all__ = ["OdooConfig", "DbConfig", "SmtpConfig"]
__odoo_config_options__ = [
    # Paths
    "data_dir",
    "backup_dir",
    "addons_dir",
    "geoip_database",
    # Registries
    "dbfilter",
    "db_name",
    # General options
    "list_db",
    "unaccent",
    "server_wide_modules",
    # Logging
    "log_handler",
]
__db_config_options__ = [
    # Database connection
    "default_maxconn",
    "default_dsn",
    "per_dbname_dsn",
    "per_dbname_maxconn",
]
__smtp_config_options__ = [
    # Server wide SMTP
    "email_from",
    "smtp_server",
    "smtp_port",
    "smtp_ssl",
    "smtp_user",
    "smtp_password",
]

import json
import logging
import os
import re
import stat
from pathlib import Path
from typing import Callable, List, Optional, Pattern

from psycopg2.extensions import make_dsn, parse_dsn

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


class InvalidOptionError(ConfigError):
    pass


class InvalidDictOptionError(InvalidOptionError):
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
        PathNotAbsoluteError(path)
    if not path.exists():
        NoSecretError(path)
    if not path.is_file():
        SecretNoFileError(path)
    if stat.S_IMODE(path.lstat().st_mode) > 0o600:
        oct_str = oct(stat.S_IMODE(path.lstat().st_mode))
        SecretOwnershipError(f"{path} ownership is {oct_str}, max allowed is `0o600`")
    return path.read_text().rstrip()


# ==============
# Config Structs
# ==============


class _OdooConfig:
    class Secrets:
        __slots__ = []  # Immutable
        admin_passwd: Callable = lambda: _read_secret("ODOOADMINPASSWORD_FILE")

    # fmt: off
    data_dir:          os.PathLike = Path("/mnt/odoo/persist")  # noqa: E241
    backup_dir:        os.PathLike = Path("/mnt/odoo/backup")  # noqa: E241
    addons_dir:        os.PathLike = Path("/mnt/odoo/addons")   # noqa: E241
    geoip_database:    os.PathLike = Path("/usr/share/GeoIP/GeoLite2-City.mmdb")  # noqa: E241
    dbfilter:              Pattern = r".*"  # noqa: E241
    db_name:   Optional[List[str]] = None  # noqa: E241
    list_db:                  bool = True  # noqa: E241
    unaccent:                 bool = True  # noqa: E241
    server_wide_modules: List[str] = ["web", "base"]  # noqa: E241
    log_handler:         List[str] = ["odoo.http.rpc.request:INFO",  # noqa: E241
                                      "odoo.http.rpc.response:INFO",
                                      ":INFO", ]
    # fmt: on


class _DbConfig:

    passfile = Path(os.environ.get("PGPASS_FILE", globals().get("DEFAULT_PGPASS_FILE")))
    _default_dsn = f"postgresql://odoo@db:5432?passfile={passfile}"

    # fmt: off
    default_maxconn:     int = 64  # noqa: E241
    default_dsn:         str = _default_dsn  # noqa: E241
    per_dbname_dsn:     dict = {}  # noqa: E241
    per_dbname_maxconn: dict = {}  # noqa: E241
    # fmt: on


class _SmtpConfig:
    class Secrets:
        __slots__ = []  # Immutable
        smtp_user: Callable = lambda: _read_secret("SMTPUSER_FILE")
        smtp_password: Callable = lambda: _read_secret("SMTPPASSWORD_FILE")

    # fmt: off
    email_from:        bool = False  # noqa: E241
    smtp_server:       bool = False  # noqa: E241
    smtp_port:          int = 25  # noqa: E241
    smtp_ssl:          bool = False  # noqa: E241
    # fmt: on


# ==============
# Config Impl.
# ==============


class _Config:
    def __init__(self, configs: List[os.PathLike]) -> None:
        """Initialize Cnfig object based on a list of dictionaries"""
        self.configs = configs
        self._load()

    def __eq__(self, other):
        """ Compare equality after hot reload"""
        if not isinstance(other, type(self)):
            # don't attempt to compare against unrelated types
            return NotImplementedError()
        return all([self[s] == other[s] for s in self.__slots__])

    def _load(self):
        for path in self.configs:
            cfg = json.load(path)
            self._cast(cfg)
            for k, v in cfg.items():
                try:
                    if not isinstance(self[k], dict):
                        self[k] = v
                        continue
                    if isinstance(v, dict):
                        self[k].update(v)
                    raise InvalidDictOptionError(f"{k} must be a dictionaty, if set.")
                except AttributeError:
                    InvalidOptionError(k)
        self._validate()

    def reload(self):
        try:
            newconfig = self.__init__(self.configs)
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

    def _validate(self):
        return


class OdooConfig(_Config, _OdooConfig):
    __slots__ = __odoo_config_options__

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


class DbConfig(_Config, _DbConfig):
    __slots__ = __db_config_options__

    def resolve_dsn(self, dbname):
        if self.per_dbname_dsn.get(dbname):
            return self.per_dbname_dsn.get(dbname)
        return self.default_dsn

    def resolve_maxconn(self, dbname):
        if self.per_dbname_maxconn.get(dbname):
            return self.per_dbname_maxconn.get(dbname)
        return self.default_maxconn

    def _cure_and_c14n(self):
        """Ensure dsn contains passfile"""

        def _ensure_dsn_with_passfile(dsn):
            dsn_dict = parse_dsn(dsn)  # Validates here as (desireable) side effect
            if not dsn_dict.get("passfile"):
                dsn_dict["passfile"] = self.passfile
            return make_dsn(dsn_dict)

        self.default_dsn = _ensure_dsn_with_passfile(self.default_dsn)
        for dbname, dsn in self.per_dbname_dsn:
            self.per_dbname_dsn[dbname] = _ensure_dsn_with_passfile(dsn)

    def _validate(self):
        """Validate values against additional constraints"""

        def _contains_no_password(dsn):
            if "password" in dsn:
                raise NoSecretsInConfigError(dsn)

        _contains_no_password(self.default_dsn)
        for _dbname, dsn in self.per_dbname_dsn:
            _contains_no_password(dsn)
        self._cure_and_c14n()


class SmtpConfig(_Config, _SmtpConfig):
    __slots__ = __smtp_config_options__

# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements the dodoo.configs api for Odoo server configuration"""


__all__ = ["load_config", "BaseConfig", "read_secret"]

import logging
import os
import stat
from pathlib import Path

from dataclasses_json import DataClassJsonMixin
from dodoo import RUNMODE
from dodoo.interfaces import odoo

from ._errors import (
    PathNotAbsoluteError,
    NoSecretError,
    SecretNoFileError,
    SecretOwnershipError,
    NoConfigDirError,
    ConfigDirNoDirError,
    ConfigDirOwnershipError,
    InvalidOptionError,
    InvalidOptionTypeError,
)

_log = logging.getLogger(__name__)

DEFAULT_ODOOADMINPASSWORD_FILE: str = "/run/secrets/adminpasswd"
DEFAULT_PGPASS_FILE: str = "/run/secrets/pgpass"
DEFAULT_SMTPUSER_FILE: str = "/run/secrets/smtpuser"
DEFAULT_SMTPPASSWORD_FILE: str = "/run/secrets/smtppassword"


# ==============
# SecOps
# ==============


def read_secret(env_var: str) -> str:
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


def load_config(config_dir, run_mode):
    _validate_confd(config_dir)

    from .db import DbConfigDevelop, DbConfigStage, DbConfigProd
    from .smtp import SmtpConfigDevelop, SmtpConfigStage, SmtpConfigProd
    from .odoo import OdooConfigDevelop, OdooConfigStage, OdooConfigProd

    class Config:
        Odoo = None
        Smtp = None
        Db = None

    if run_mode == RUNMODE.Develop:
        Config.Odoo = OdooConfigDevelop.load(config_dir)
        Config.Db = DbConfigDevelop.load(config_dir)
        Config.Smtp = SmtpConfigDevelop.load(config_dir)
    elif run_mode == RUNMODE.Staging:
        Config.Odoo = OdooConfigStage.load(config_dir)
        Config.Db = DbConfigStage.load(config_dir)
        Config.Smtp = SmtpConfigStage.load(config_dir)
    elif run_mode == RUNMODE.Production:
        Config.Odoo = OdooConfigProd.load(config_dir)
        Config.Db = DbConfigProd.load(config_dir)
        Config.Smtp = SmtpConfigProd.load(config_dir)
    else:
        raise Exception()  # Never hit
    return Config


class BaseConfig(DataClassJsonMixin):
    @staticmethod
    def _cure(cfg: dict):
        return

    @classmethod
    def load(cls, confd: os.PathLike):
        cls.confd = confd
        cfg = {}
        for child in cls.confd.iterdir():
            if child.name == cls._file_name:
                cfg = cls.from_json(child.read_text)
                cls._cure(cfg)
                break
        try:
            return cls.__new__(cls, **cfg)
        except TypeError as e:
            raise InvalidOptionError(e.args[0])

    def __post_init__(self, *args, **kwargs):
        self._validate()

    def reload(self):
        try:
            newconfig = self.__class__.load(self.confd)
            if self != newconfig:
                _log.info(f"Updated {self.__name__}.")
                self = newconfig
                return True
            else:
                return False
        except Exception:
            _log.warning(f"Hot reload of {self.__name__} failed.")
            return False

    def apply(self):
        cfg = odoo.Config()
        for k, v in self.__dict__:
            cfg.config[k] = v

    def _validate(self):
        for k, v in self.__dict__.items():
            orig_type = self.__dataclass_fields__[k].type
            if orig_type == type(v):
                continue
            msg = (
                f"Type '{type(v).__qualname__}' does not "
                f"conform to '{orig_type.__qualname__}'"
            )
            InvalidOptionTypeError(msg)
        return

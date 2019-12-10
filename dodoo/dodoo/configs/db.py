# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the database configuration"""

import logging
import os
from pathlib import Path
from typing import Mapping

from psycopg2.extensions import make_dsn, parse_dsn

from dataclasses import dataclass, field

from . import BaseConfig
from ._errors import NoSecretsInConfigError

_log = logging.getLogger(__name__)

DEFAULT_PGPASS_FILE: str = "/run/secrets/pgpass"

passfile = Path(os.environ.get("PGPASS_FILE", globals().get("DEFAULT_PGPASS_FILE")))


@dataclass(frozen=True)
class DbConfig(BaseConfig):
    _default_dsn = f"user=odoo host=db port=5432 passfile={passfile}"
    odoo_schema = "odoo"
    dodoo_schema = "dodoo"
    # fmt: off
    default_maxconn:     int = 64  # noqa: E241
    default_dsn:         str = _default_dsn  # noqa: E241
    per_dbname_dsn:     Mapping[str, str] = field(default_factory=dict)  # noqa: E241
    per_dbname_maxconn: Mapping[str, str] = field(default_factory=dict)  # noqa: E241
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

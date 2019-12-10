# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the server wide fallback smtp configuration"""

import logging

from dataclasses import InitVar, dataclass

from . import BaseConfig, read_secret

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SmtpConfig(BaseConfig):

    validate: InitVar[bool] = True

    # fmt: off
    email_from:   bool = False  # noqa: E241
    server:       bool = False  # noqa: E241
    port:          int = 25  # noqa: E241
    ssl:          bool = True  # noqa: E241

    # Secrets
    class Sec():
        __slots__ = []  # Immutable
        user = lambda self: read_secret("SMTPUSER_FILE")  # noqa: E731
        password = lambda self: read_secret("SMTPPASSWORD_FILE")  # noqa: E731
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

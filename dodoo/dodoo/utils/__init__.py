# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This a bad package: it's called utils."""


import logging
import dodoo
from functools import wraps

_log = logging.getLogger(__name__)


class FrameworkNotInitialized(Exception):
    pass


def ensure_framework(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        framework = dodoo.framework()
        if not framework:
            _log.critical("dodoo must initialize the framework first.")
            raise FrameworkNotInitialized()
        return f(*args, **kwds)

    return wrapper

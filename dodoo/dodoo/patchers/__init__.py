# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements patcher machinery for frameworks to suck less"""

__version__ = "0.0.1"
__all__ = ["BasePatcher", "PatchableProperty"]

import importlib
import logging

from functools import wraps

_log = logging.getLogger(__name__)


class PatchError(RuntimeError):
    pass


class BasePatcher:
    """An implementation of BasePatcher, together with an implementation of an
    interface declaring PatchableProperties patches a namespace.

    Usage:
        Inheriting patchers also inherit an interface class which declares
        PatchableProperties: If the patcher declares an attribute of the same
        name of a PatchableProperty on the interface class, the corresponding
        namespace will be automatically patched by a call to `apply()`.

        Feature switches can be set on the `cls` to modify the patch set during
        run time."""

    features = {}

    @staticmethod
    def onFeature(feature):
        """ This decorator set's a feature flag selector on a patch method."""

        def decorator(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                fn(*args, **kwargs)

            decorated.onFeature = feature
            return decorated

        return decorator

    @staticmethod
    def unlessFeature(feature):
        """ This decorator set's a feature flag selector on a patch method."""

        def decorator(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                fn(*args, **kwargs)

            decorated.unlessFeature = feature
            return decorated

        return decorator

    def apply(self):
        for attr in self.__dict__.values():
            if not isinstance(getattr(super(), attr, None), PatchableProperty):
                _log.debug(
                    f"Skipping {attr}: not defined or not as PatchableProperty "
                    "on the interface base class (or no interface base class "
                    "defined)."
                )
                continue
            if hasattr(attr, "onFeature"):
                if getattr(attr, "onFeature") not in self.features:
                    _log.info(
                        f"Skipping {attr} as feature '{attr.onFeature}' is "
                        "not enabled."
                    )
                    continue
            if hasattr(attr, "unlessFeature"):
                if getattr(attr, "unlessFeature") in self.features:
                    _log.info(
                        f"Skipping {attr} as feature '{attr.unlessFeature}' is "
                        "enabled."
                    )
                    continue
            try:
                setattr(super(), attr, getattr(self, attr))
            except Exception:
                msg = f"Patch {attr} not applied"
                _log.ciritcal(msg)
                raise PatchError(msg)
            else:
                target = super().__dict__[attr].obj_path
                _log.info(f"{target} patched. ")


class PatchableProperty(object):
    def __init__(self, obj_path):
        self.obj_path = obj_path
        self.mod_path = obj_path.rpartition(":")[0]
        self.obj = obj_path.rpartition(":")[2]

    def __get__(self, obj, klass=None):
        module = importlib.import_module(self.mod_path)
        obj = self.obj.rpartition(".")[2]
        base = self.obj.rpartition(".")[0]
        if base:
            return getattr(getattr(module, base), obj)
        return getattr(module, obj)

    def __set__(self, obj, value):
        module = importlib.import_module(self.mod_path)
        obj = self.obj.rpartition(".")[2]
        base = self.obj.rpartition(".")[0]
        if base:
            base = getattr(module, base)
            setattr(base, obj, value)
        else:
            setattr(module, obj, value)

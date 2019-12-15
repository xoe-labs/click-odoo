# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements patcher machinery for frameworks to suck less"""

__version__ = "0.0.1"
__all__ = ["BasePatcher", "PatchableProperty"]

import importlib
import logging
import inspect

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
                return fn(*args, **kwargs)

            decorated.onFeature = feature
            return decorated

        return decorator

    @staticmethod
    def unlessFeature(feature):
        """ This decorator set's a feature flag selector on a patch method."""

        def decorator(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                return fn(*args, **kwargs)

            decorated.unlessFeature = feature
            return decorated

        return decorator

    def get_patchable_property_obj(self, name, log=True):
        Patchable = type(self).__mro__[1]
        try:
            candidate = Patchable.__getattribute__(Patchable, name)
            if log:
                _log.debug(f"{Patchable} got attribute '{name}'.")
            if isinstance(candidate, PatchableProperty):
                return candidate
            else:
                return None
        except AttributeError:
            if log:
                _log.debug(f"{Patchable} got no attribute '{name}'.")
            return None

    def _predicate(self, member):
        try:
            name = member.__name__
        except AttributeError:
            return False
        if name.startswith("__"):
            return False
        return bool(self.get_patchable_property_obj(name))

    def _prop_predicate(self, member):
        if isinstance(member, property):
            return True
        return False

    def apply(self):
        Patchable = type(self).__mro__[1]
        members = inspect.getmembers(self, predicate=self._predicate)
        members.extend(inspect.getmembers(type(self), predicate=self._prop_predicate))
        if not members:
            return
        for attr, candidate in members:
            isproperty = False
            if isinstance(candidate, property):
                isproperty = True
            if not isproperty and attr != candidate.__name__:
                # predicate function has only access to the member, not under
                # which name it's registered
                _log.debug(
                    f"Attribute '{attr}' has assigned {candidate}. By chance, it "
                    f"shares name ('{candidate.__name__}'') with "
                    f"a patchable attribute of {Patchable}, but it's not a "
                    "intented for patching. Skipping..."
                )
                continue
            _cand = candidate.fget if isproperty else candidate
            # Feature flags
            onFeature = getattr(_cand, "onFeature", None)
            unlessFeature = getattr(_cand, "unlessFeature", None)
            if onFeature and not self.features.get(onFeature, None):
                msg = f"Skipping {attr} as feature '{onFeature}' is " "not enabled."
                _log.info(msg)
                continue
            if unlessFeature and self.features.get(unlessFeature, None):
                msg = f"Skipping {attr} as feature '{unlessFeature}' is " "enabled."
                _log.info(msg)
                continue
            #
            try:
                patchable_prop = self.get_patchable_property_obj(attr, log=False)
                if isinstance(candidate, property):
                    setattr(Patchable(), attr, _cand(attr))
                else:
                    setattr(Patchable(), attr, _cand)
            except Exception:
                msg = f"Patch {attr} not applied"
                _log.ciritcal(msg)
                raise PatchError(msg)
            else:
                _log.info(f"{patchable_prop.obj_path} patched. ")


class PatchableProperty(object):
    def __init__(self, obj_path):
        self.obj_path = obj_path
        self.mod_path = obj_path.rpartition(":")[0]
        self.obj = obj_path.rpartition(":")[2]

    def __get__(self, obj, type=None):
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

# =============================================================================
# Created By : David Arnold
# Credits    : Stéphane Bidoul, Thomas Binsfeld, Benjamin Willig
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements common utilities not provided by the frameworks"""

from dodoo.interfaces import odoo

# Adopted from acsone/click-odoo


class ModuleNotFound(Exception):
    pass


def expand_dependencies(modules, include_auto_install=True):
    """ Given a set od modules, returns a sorted list of all transitive
    dependencies. By default, `auto_install = True`  modules are included, too.
    """
    odoo.Modules().initialize_sys_path()

    res = set()

    def add_deps(module):
        if module in res:
            return
        res.add(module)
        manifest = odoo.Modules().parse_manifest_from(module)
        if not manifest:
            raise ModuleNotFound(module)
        for dep in manifest.get("depends", ["base"]):
            add_deps(dep)

    for module in modules:
        add_deps(module)

    if not include_auto_install:
        return sorted(list(res))

    auto_install_list = []
    for module in sorted(odoo.Modules().all_modules()):
        manifest = odoo.Modules().parse_manifest_from(module)
        if manifest.get("auto_install"):
            auto_install_list.append((module, manifest))

    recurse = True
    while recurse:
        recurse = False
        for module, manifest in auto_install_list:
            if module in res:
                continue
            # if not all dependencies of auto_install module are
            # installed we skip it
            depends = set(manifest.get("depends", ["base"]))
            if not depends.issubset(res):
                continue
            # all dependencies of auto_install module are
            # installed so we add it
            add_deps(module)
            # recurse, in case an auto_install module depends
            # on other auto_install modules
            recurse = True
    return sorted(list(res))

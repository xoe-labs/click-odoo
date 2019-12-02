# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements odoo watcher file handler"""

import dodoo.interfaces.odoo as odoo
import ast
import importlib

import logging
from pathlib import Path

_log = logging.getLogger(__name__)


def _get_odoo_models_from_file(path):
    model_names_in_file = []
    with path.open("r") as f:
        doc = ast.parse(f.read())
        for node in ast.walk(doc):
            if not isinstance(node, ast.ClassDef):
                continue
            klass = node
            name = None
            inherit = None
            for child in klass.body:
                if not isinstance(child, ast.Assign):
                    continue
                assign = child
                for target in assign.targets:
                    if target.id == "_name":
                        name = assign.value.id
                    if target.id == "_inherit":
                        if not isinstance(target, ast.Name):
                            continue
                        inherit = assign.value.id
            if name or inherit:
                model_names_in_file.append(name or inherit)
    return model_names_in_file


def file_changed(self, path):
    if path not in self.changed_paths:
        self.changed_paths.add(path)
        self.logger.info(f"{path} changed; handling it ...")

    module_name, relpath = odoo.Modules().deduce_module_and_relpath_from(path)
    info = odoo.Modules().parse_manifest_from(module_name) if module_name else None

    if not module_name:
        self.set_changed()

    # #############
    # Module scoped
    # #############

    res = _deduced_actions(path, module_name, relpath, info)

    if "update_module_list" in res:
        for registry in odoo.Registry.items():
            registry["ir.module.module"].update_list()

    if res["model_names_in_file"]:
        importlib.reload("odoo.addons." + module_name)  # Rebuild, then ...
        odoo.Modules().loaded.remove(module_name)  # .... purge from ref tabel ...
        odoo.Modules().load(module_name)  # ... so we can re-init
        # NOTE: a second module which imports from this module
        # using from odoo.adons.module... import ... still has the old
        # objects referenced and therefore will not see the code change (see
        # importlib.reload for details). This is extremly rare, and when
        # strange things happen users are expected to reload manually.
        # This behaviour fixes the problem.
        # TODO: detect a schema change -> trigger module upgrade
        for registry in odoo.Registry.items():
            if module_name not in registry._init_modules:
                continue
            registry = odoo.modules.Registry.new(registry.db_name)
            with registry.cursor() as cr:
                registry.init_models(cr, res["model_names_in_file"])

    if "update" in res:
        for registry in odoo.Registry.items():
            if module_name not in registry._init_modules:
                continue
            (
                registry["ir.module.module"]
                .search([("name", "=", module_name), ("state", "=", "installed")])
                .write({"state", "=", "to upgrade"})
            )
        self.set_changed()


def _deduced_actions(path, module_name, relpath, info):

    path = Path(path)
    res = {}
    model_names_in_file = []
    # Python files
    if path.suffix == ".py" and not path.name.startswith(".~"):
        if path.name in odoo.Modules().MANIFEST_NAMES:
            res["update_module_list"] = True
        else:
            model_names_in_file += _get_odoo_models_from_file(path)
    # Something else, but referenced in the manifest -> upgrade module
    elif relpath and (
        relpath in info.get("data")
        or relpath in info.get("demo")
        and module_name in odoo.Config().config["demo"]
        or odoo.Config().config["demo"] == "all"
    ):
        if not relpath.startswith("view"):
            res["update"] = True
    res["model_names_in_file"] = model_names_in_file
    return res

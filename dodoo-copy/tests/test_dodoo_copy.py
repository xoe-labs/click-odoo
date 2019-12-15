import logging

import pytest
from dodoo_copy import __version__, copy
from dodoo_init import init


def test_version():
    assert __version__ == "0.1.0"


@pytest.fixture
def init_odoo(db, newdb, main_loaded):
    modules = ["base"]
    with_demo = True
    no_cache = False
    init(modules, with_demo, no_cache, newdb)
    yield newdb


def test_copy_and_install_modules(init_odoo, newdb2, caplog):
    modules = ["base_address_city"]
    force_disconnect = True
    from_db = init_odoo
    new_db = newdb2

    caplog.set_level(logging.INFO)
    copy(modules, force_disconnect, from_db, new_db)
    assert (
        "module base_address_city: creating or updating database tables" in caplog.text
    )
    assert "updating modules list" in caplog.text
    assert f"Database and filestore copied from {from_db} to {new_db}." in caplog.text
    assert f"Additional module(s) {','.join(modules)} installed." in caplog.text

    from dodoo.interfaces import odoo

    # We are naively (not really) verifying shutil itself here
    # (basically, just check somehow if that call was made)
    fs_from = odoo.Config().filestore(from_db)
    fs_new = odoo.Config().filestore(new_db)
    for path in fs_from.iterdir():
        assert (fs_new / path).exists()

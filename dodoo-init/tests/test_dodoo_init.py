import logging

from dodoo_init import __version__, addons_digest, init, trim_cache


def test_version():
    assert __version__ == "0.1.0"


def test_addons_digest(main_loaded, caplog):
    hash_without_demo = addons_digest(["base", "mail"], True)
    assert addons_digest(["base", "mail"], False) != hash_without_demo
    caplog.set_level(logging.DEBUG)
    assert addons_digest(["base", "mail"], True) == hash_without_demo
    assert "base" in caplog.text
    assert "bus" in caplog.text
    assert "mail" in caplog.text
    assert "iap" in caplog.text
    assert "web" in caplog.text


def test_odoo_createdb_init_and_cache(db, newdb, newdb2, main_loaded, caplog):
    caplog.set_level(logging.INFO)
    init(modules=["base"], with_demo=True, no_cache=False, database=newdb)
    assert "loading base" in caplog.text
    assert f"New database '{newdb}' created." in caplog.text
    assert f"Demo data in '{newdb}' loaded." in caplog.text
    assert f"Database '{newdb}' put in db cache." in caplog.text
    caplog.clear()
    init(modules=["base"], with_demo=True, no_cache=False, database=newdb2)
    assert "loading base" not in caplog.text
    assert f"New database '{newdb2}' created." not in caplog.text
    assert f"Demo data in '{newdb2}' loaded." not in caplog.text
    assert f"New database '{newdb2}' created from db cache." in caplog.text
    caplog.clear()
    trim_cache(max_age=None, max_size=0)
    # Trimming with max_size ...
    assert f"1 database(s) cleared from cache (max-size)." in caplog.text
    # ... yet, max_age codepath should NOT have executed (max_age = None).
    assert "(max-age)." not in caplog.text
    caplog.clear()
    trim_cache(max_age=0, max_size=None)
    # Nothing left to trim ...
    assert f"No database cleared from cache (max-age)." in caplog.text
    # ... yet, max_size codepath should NOT have executed (max_size = None).
    assert f"(max-size)." not in caplog.text

import logging

import pytest
from dodoo_init import init
from dodoo_run import __version__, bus, cron, graphql, http, queue


def test_version():
    assert __version__ == "0.1.0"


@pytest.fixture
def init_odoo(db, newdb, main_loaded):
    modules = ["base"]
    with_demo = True
    no_cache = False
    init(modules, with_demo, no_cache, newdb)
    yield newdb


def test_http(init_odoo, caplog):
    caplog.set_level(logging.INFO)
    http("127.0.0.1", 8069)

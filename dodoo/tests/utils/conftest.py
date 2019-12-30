import pytest
from psycopg2.extensions import make_dsn
from pytest_postgresql import factories

postgres = factories.postgresql_proc()
pg_conn_main = factories.postgresql("postgres")
pg_conn_test = factories.postgresql("postgres", db_name="test")


@pytest.fixture()
def main_loaded(confd, project_version_file, framework_dir, mocker):
    import dodoo
    from dodoo import RUNMODE, main

    orig_framework = dodoo._framework
    mocker.patch("dodoo.create_custom_schema_layout")
    main(framework_dir, confd, False, RUNMODE.Production, 0, None, project_version_file)
    yield
    dodoo._framework = orig_framework


@pytest.fixture
def db(pg_conn_main, pg_conn_test, mocker):
    dsn_params = pg_conn_main.info.dsn_parameters
    mocker.patch("dodoo.utils.db._dsn_resolver", lambda _: make_dsn(**dsn_params))
    yield pg_conn_test.info.dbname


@pytest.fixture()
def fs(main_loaded):
    dbname = "testdb"
    from dodoo.interfaces import odoo

    fs = odoo.Config().filestore(dbname)
    fs.mkdir(parents=True)
    yield fs
    if fs.exists():
        fs.rmdir()

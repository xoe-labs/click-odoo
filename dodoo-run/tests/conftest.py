import json
import os
import shutil
from pathlib import Path
from textwrap import dedent

import dodoo_init.cache as cache
import pytest
from psycopg2.extensions import make_dsn
from pytest_postgresql import factories

postgres = factories.postgresql_proc()
pg_conn_main = factories.postgresql("postgres")
pg_conn_test = factories.postgresql("postgres", db_name="test")


@pytest.fixture(autouse=True, scope="package")
def environ(tmp_path_factory) -> None:
    secrets = tmp_path_factory.mktemp("secrets")
    admin_passwd = secrets / "admin"
    admin_passwd.write_text("admin-pwd")
    admin_passwd.chmod(0o500)
    session_encryption_key = secrets / "sessionencryptionkey"
    session_encryption_key.write_text("secret-key")
    session_encryption_key.chmod(0o500)
    smtpuser = secrets / "smtpuser"
    smtpuser.write_text("smtp-user")
    smtpuser.chmod(0o500)
    smtppwd = secrets / "smtppwd"
    smtppwd.write_text("smtp-pwd")
    smtppwd.chmod(0o500)
    os.environ.update(ODOOADMINPASSWORD_FILE=str(admin_passwd))
    os.environ.update(SESSION_ENCRYPTION_KEY_FILE=str(session_encryption_key))
    os.environ.update(SMTPUSER_FILE=str(smtpuser))
    os.environ.update(SMTPPASSWORD_FILE=str(smtppwd))
    secrets.chmod(0o500)
    yield
    secrets.chmod(0o777)


@pytest.fixture(scope="session")
def framework_dir() -> Path:
    return Path("../.odoo").resolve()


@pytest.fixture(scope="session")
def original_global_datadir():
    return Path(os.path.realpath(__file__)).parent / "data"


def prep_global_datadir(tmp_path_factory, original_global_datadir):
    temp_dir = tmp_path_factory.mktemp("data") / "datadir"
    shutil.copytree(original_global_datadir, temp_dir)
    return temp_dir


@pytest.fixture(scope="session")
def global_datadir(tmp_path_factory, original_global_datadir):
    return prep_global_datadir(tmp_path_factory, original_global_datadir)


@pytest.fixture(scope="module")
def confd(global_datadir, tmp_path_factory) -> Path:
    datadir = global_datadir / "confd"
    develop = datadir / "odooconfig.develop.json"
    stage = datadir / "odooconfig.stage.json"
    prod = datadir / "odooconfig.prod.json"

    develop_dict = json.loads(develop.read_text())
    stage_dict = json.loads(stage.read_text())
    prod_dict = json.loads(prod.read_text())

    persist_dir = tmp_path_factory.mktemp("persist")
    backup_dir = tmp_path_factory.mktemp("backup")
    addons_dir = tmp_path_factory.mktemp("addons")
    scoped_addons_dir = tmp_path_factory.mktemp("scoped_addons")
    geoip_database_dir = tmp_path_factory.mktemp("geoip_database")
    geoip_database_file = geoip_database_dir / "GeoLite2-City.mmdb"
    geoip_database_file.touch()

    upd = {
        "data_dir": str(persist_dir),
        "backup_dir": str(backup_dir),
        "addons_dir": str(addons_dir),
        "scoped_addons_dir": str(scoped_addons_dir),
        "geoip_database": str(geoip_database_file),
    }
    develop_dict.update(**upd)
    stage_dict.update(**upd)
    prod_dict.update(**upd)

    with develop.open(mode="w") as f:
        f.write(json.dumps(develop_dict))
    with stage.open(mode="w") as f:
        f.write(json.dumps(stage_dict))
    with prod.open(mode="w") as f:
        f.write(json.dumps(prod_dict))

    datadir.chmod(0o550)
    yield datadir
    datadir.chmod(0o777)


@pytest.fixture(autouse=True, scope="package")
def project_version_file(tmp_path_factory) -> Path:
    project = tmp_path_factory.mktemp("project")
    version = project / "version"
    version.write_text("v0.1.0")
    return version


@pytest.fixture(scope="package")
def graphql_schema(tmp_path_factory) -> Path:
    graphql = tmp_path_factory.mktemp("graphql")
    schema = graphql / "schema"
    schema.write_text(
        dedent(
            """
        type Planet implements Node {
          id: ID!
          createdAt: DateTime!
          updatedAt: DateTime
          name: String
          description: String
          planetType: PlanetTypeEnum
        }
        input CreatePlanetInput {
          name: String!
          galaxyId: ID!
          description: String
        }
        type Mutation {
          createPlanet(input: CreatePlanetInput!): Planet!
        }
    """
        )
    )
    return schema


@pytest.fixture()
def main_loaded(confd, project_version_file, framework_dir, mocker):
    import dodoo
    from dodoo import RUNMODE, main

    orig_framework = dodoo._framework
    mocker.patch("dodoo.create_custom_schema_layout")
    main(framework_dir, confd, False, RUNMODE.Develop, 0, project_version_file)
    yield
    dodoo._framework = orig_framework


@pytest.fixture
def db(pg_conn_main, pg_conn_test, mocker):
    dsn_params = pg_conn_main.info.dsn_parameters
    mocker.patch(
        "dodoo.configs.db.DbConfig.resolve_dsn", lambda *args: make_dsn(**dsn_params)
    )
    # also avoid @ensure_framework decorator:
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


@pytest.fixture
def dbcache(db):
    import dodoo

    dodoo.utils.db.terminate_connections(db)
    dsn = dodoo.utils.db.maintenance_dsn()
    with cache.DbCache(dsn, "cachetest") as c:
        yield c


def _dropdb(name, pg_conn_main):
    pg_conn_main.autocommit = True
    import dodoo

    dodoo.utils.db.terminate_connections(name)
    with pg_conn_main.cursor() as cr:
        cr.execute(f'DROP DATABASE IF EXISTS "{name}"')
    pg_conn_main.autocommit = False


@pytest.fixture
def newdb(db, pg_conn_main):
    name = db + "new"
    yield name
    _dropdb(name, pg_conn_main)


@pytest.fixture
def newdb2(db, pg_conn_main):
    name = db + "new2"
    yield name
    _dropdb(name, pg_conn_main)

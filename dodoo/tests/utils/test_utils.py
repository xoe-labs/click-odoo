import pytest
from psycopg2.extensions import make_dsn
from pytest_postgresql import factories

import dodoo.utils as utils
import dodoo.utils.db as dbutils
import dodoo.utils.odoo as odooutils
from dodoo.interfaces import odoo


class TestUtils:
    def test_ensure_framework_fails(self):
        @utils.ensure_framework
        def dummy():
            pass

        with pytest.raises(utils.FrameworkNotInitialized):
            dummy()

    def test_ensure_framework(self, main_loaded):
        @utils.ensure_framework
        def dummy():
            pass

        assert dummy() is None


postgres = factories.postgresql_proc()
pg_conn_main = factories.postgresql("postgres")
pg_conn_test = factories.postgresql("postgres", db_name="test")


class TestDbUtils:
    def test_maintenance_dsn(self, main_loaded):
        assert (
            "user=odoo passfile=/run/secrets/pgpass host=db port=5432"
            == dbutils.maintenance_dsn()
        )
        args = dbutils._maint_conn_args()
        assert "-h" in args
        assert "-U" in args
        assert "-p" in args
        assert "--no-password" in args

    @pytest.fixture
    def db(self, pg_conn_main, pg_conn_test, mocker):
        dsn_params = pg_conn_main.info.dsn_parameters
        mocker.patch("dodoo.utils.db._dsn_resolver", lambda _: make_dsn(**dsn_params))
        yield pg_conn_test.info.dbname

    def test_db_exists_sql(self, db):
        assert dbutils.db_exists(db)
        assert not dbutils.db_exists("no-" + db)

    def test_terminate_connections_sql(self, db):
        assert dbutils.db_exists(db)
        assert dbutils.terminate_connections(db) == 1

    def test_drop_database(self, main_loaded, db):
        assert dbutils.terminate_connections(db) == 1
        dbutils.drop_database(db)
        assert not dbutils.db_exists(db)

    def test_copy_db(self, main_loaded, db):
        assert dbutils.terminate_connections(db) == 1
        copy = db + "copy"
        dbutils.copy_db(db, copy)
        assert dbutils.db_exists(copy)

    def test_backup_restore_database(self, main_loaded, db, tmp_path):
        assert dbutils.terminate_connections(db) == 1
        restore = db + "restored"
        file = tmp_path / "tempfile"
        dbutils.backup_database(db, file)
        dbutils.restore_database(restore, file)
        assert dbutils.db_exists(restore)


class TestOdooUtils:
    @pytest.fixture()
    def fs(self, main_loaded):
        dbname = "testdb"
        fs = odoo.Config().filestore(dbname)
        fs.mkdir(parents=True)
        yield fs
        if fs.exists():
            fs.rmdir()

    def test_drop_filestore(self, fs):
        db = fs.name
        odooutils.drop_filestore(db)
        assert not fs.exists()

    def test_copy_filestore(self, fs):
        db = fs.name
        new_db = fs.name + "new"
        odooutils.copy_filestore(db, new_db)
        assert (fs.parent / new_db).exists()

    def test_backup_restore_filestore(self, fs, tmp_path):
        db = fs.name
        bkp = tmp_path / "bkp"
        odooutils.backup_filestore(db, bkp)
        odooutils.drop_filestore(db)
        assert not fs.exists()
        odooutils.restore_filestore(db, bkp)
        assert fs.exists()

    def test_expand_dependencies(self, main_loaded):
        res = odooutils.expand_dependencies(
            ["auth_signup", "base_import"], include_auto_install=False
        )
        assert "auth_signup" in res
        assert "mail" in res  # dependency of auth_signup
        assert "base_import" in res
        assert "base" in res  # obviously
        assert "web" in res  # base_import depends on web
        assert "iap" not in res  # iap is auto_install

    def test_expand_dependencies_auto_install(self, main_loaded):
        res = odooutils.expand_dependencies(["auth_signup"])
        assert "auth_signup" in res
        assert "base" in res  # obviously
        assert "iap" in res  # iap is auto_install
        assert "web" in res  # web is autoinstall
        assert "base_import" in res  # base_import is indirect autoinstall

    def test_expand_dependencies_not_found(self, main_loaded):
        with pytest.raises(odooutils.ModuleNotFound):
            odooutils.expand_dependencies(["not_a_module"])

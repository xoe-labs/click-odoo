import json
import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="package")
def environ(tmp_path_factory) -> None:
    secrets = tmp_path_factory.mktemp("secrets")
    admin_passwd = secrets / "admin"
    admin_passwd.write_text("admin-pwd")
    admin_passwd.chmod(0o500)
    smtpuser = secrets / "smtpuser"
    smtpuser.write_text("smtp-user")
    smtpuser.chmod(0o500)
    smtppwd = secrets / "smtppwd"
    smtppwd.write_text("smtp-pwd")
    smtppwd.chmod(0o500)
    os.environ.update(ODOOADMINPASSWORD_FILE=str(admin_passwd))
    os.environ.update(SMTPUSER_FILE=str(smtpuser))
    os.environ.update(SMTPPASSWORD_FILE=str(smtppwd))
    secrets.chmod(0o500)
    yield
    secrets.chmod(0o777)


@pytest.fixture()
def confd(datadir, tmp_path_factory) -> Path:
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
    yield version

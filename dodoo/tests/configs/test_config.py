import json
import logging
from pathlib import Path

import pytest

from dodoo import RUNMODE
from dodoo.configs import load_config, read_secret
from dodoo.configs._errors import (
    ConfigDirNoDirError,
    ConfigDirOwnershipError,
    NoConfigDirError,
    NoPathError,
)


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


class TestConfig:
    def test_confd_path(self, tmp_path):
        with pytest.raises(NoConfigDirError):
            fakepath = tmp_path / "fakepath"
            load_config(fakepath, RUNMODE.Production)
        with pytest.raises(ConfigDirNoDirError):
            file = tmp_path / "file"
            file.touch()
            load_config(file, RUNMODE.Production)
        with pytest.raises(ConfigDirOwnershipError):
            tmp_path.chmod(0o555)
            load_config(tmp_path, RUNMODE.Production)

    def test_confd_content(self, tmp_path, caplog):
        caplog.set_level(logging.WARNING)
        (tmp_path / "some-dir").mkdir()
        (tmp_path / "some-none-json-file").touch()
        tmp_path.chmod(0o550)
        with pytest.raises(NoPathError):  # Default paths still don't exist
            load_config(tmp_path, RUNMODE.Production)
        assert len(caplog.records) == 2
        assert "some-dir" in caplog.text
        assert "some-none-json-file" in caplog.text

    def test_confd_config(self, confd, caplog):
        # confd fixture is holding a duly preparated config dir
        # No warnings or critical logs should occur
        caplog.set_level(logging.WARNING)
        load_config(confd, RUNMODE.Production)
        assert len(caplog.records) == 0

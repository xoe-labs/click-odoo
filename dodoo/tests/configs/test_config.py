import logging

import pytest

from dodoo import RUNMODE
from dodoo.configs import load_config
from dodoo.configs._errors import (
    ConfigDirNoDirError,
    ConfigDirOwnershipError,
    NoConfigDirError,
    NoPathError,
)


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

    def test_read_secret(self, confd, caplog):
        # confd fixture is holding a duly preparated config dir
        # No warnings or critical logs should occur
        caplog.set_level(logging.WARNING)
        config = load_config(confd, RUNMODE.Production)
        assert "admin-pwd" == config.Odoo.Sec.admin_passwd
        assert "smtp-user" == config.Smtp.Sec.user
        assert "smtp-pwd" == config.Smtp.Sec.password
        assert len(caplog.records) == 0

    def test_odoo_config_apply(self, confd, caplog):
        caplog.set_level(logging.WARNING)
        config = load_config(confd, RUNMODE.Production)
        config.Odoo.apply()
        assert len(caplog.records) == 0

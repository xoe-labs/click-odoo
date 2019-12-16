import logging
import shutil
from datetime import datetime
from pathlib import Path

import pytest
from dodoo_backup import FolderStructureUnkown, __version__, _extracted, backup, restore
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


@pytest.fixture
def bkpdir(tmp_path):
    bkpdir = tmp_path / "backup"
    bkpdir.mkdir()
    yield bkpdir


# Keep in one test as database setup is (unfortunately) function scope
# it also takes a bit of time ...
def test_backup_restore(bkpdir, tmp_path, init_odoo, newdb2, caplog, mocker):
    caplog.set_level(logging.INFO)
    dbname = "notexists"
    backup(filestore_include=True, dbname=dbname, dest=bkpdir)
    assert f"Database {dbname} doesn't exists." in caplog.text
    caplog.clear()
    dt = mocker.patch("dodoo_backup.datetime")
    now = datetime.now()
    dt.now.return_value = now
    dt.isoformat.return_value = datetime.isoformat(now, timespec="seconds")
    archive = backup(filestore_include=True, dbname=init_odoo, dest=bkpdir)
    assert archive.parent == bkpdir
    assert datetime.isoformat(now, timespec="seconds") in str(archive)
    caplog.clear()

    dbname = newdb2
    # Restore normally
    restore(clear=False, dbname=dbname, src=archive)
    assert f"Database & filestore {dbname} restored." in caplog.text
    caplog.clear()

    from dodoo.interfaces import odoo

    # We are naively (not really) verifying shutil itself here
    # (basically, just check somehow if that call was made)
    fs_from = odoo.Config().filestore(init_odoo)
    fs_new = odoo.Config().filestore(dbname)
    for path in fs_from.iterdir():
        assert (fs_new / path).exists()

    # Restore already exists
    restore(clear=False, dbname=dbname, src=archive)
    assert f"Database {dbname} already exists." in caplog.text
    caplog.clear()

    # Restore already exists with clear
    restore(clear=True, dbname=dbname, src=archive)
    assert f"Dropping database & filestore of {dbname} before restoring." in caplog.text
    assert f"Database & filestore {dbname} pruned." in caplog.text
    assert f"Database & filestore {dbname} restored." in caplog.text
    caplog.clear()

    # Ensure corrupted archives fail before deleting target database.
    with _extracted(archive) as dir:
        db_bkp = dir / "db.dump"
        db_bkp.rename(db_bkp.parent / "wrongname.dump")
        newarchive = dir / "corrupted_archive"
        newarchive = Path(shutil.make_archive(newarchive, "gztar", dir))
        # Restore already exists with clear
        with pytest.raises(FolderStructureUnkown):
            restore(clear=True, dbname=dbname, src=newarchive)
    assert (
        f"Dropping database & filestore of {dbname} before restoring."
        not in caplog.text
    )
    assert f"Database & filestore {dbname} pruned." not in caplog.text
    assert f"Database & filestore {dbname} restored." not in caplog.text
    caplog.clear()

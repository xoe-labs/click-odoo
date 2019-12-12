# =============================================================================
# Created By : David Arnold
# Credits    : Stéphane Bidoul, Thomas Binsfeld, Benjamin Willig
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo init cache"""

import contextlib
import hashlib
import logging
from datetime import datetime

from dodoo.connections import PublicCursor

_log = logging.getLogger(__name__)


class DbCache(PublicCursor):
    """ Manage a cache of db templates.

    Templates are named prefix-YYYYmmddHHMM-hashsum, where
    YYYYmmddHHMM is the date and time when the given hashsum has last been
    used for that prefix.
    """

    HASH_SIZE = hashlib.sha1().digest_size * 2
    MAX_HASHSUM = "f" * HASH_SIZE

    def __init__(self, dsn, prefix, dry=False):
        super().__init__(dsn, dry)
        self.prefix = prefix
        self.lock_id = self._make_lock_id()

    def __enter__(self):
        cr = super().__enter__(self)
        cr.autocommit(True)
        return self

    def _make_lock_id(self):
        # try to make a unique lock id based on the cache prefix
        h = hashlib.sha1()
        h.update(self.prefix.encode("utf8"))
        return int(h.hexdigest()[:14], 16)

    @contextlib.contextmanager
    def _lock(self):
        self.cr.execute("SELECT pg_advisory_lock(%s::bigint)", (self.lock_id,))
        try:
            yield
        finally:
            self.cr.execute("SELECT pg_advisory_unlock(%s::bigint)", (self.lock_id,))

    def _make_pattern(self, dt=None, hs=None):
        if dt:
            dtpart = dt.strftime("%Y%m%d%H%M")
        else:
            dtpart = "_" * 12
        if hs:
            hspart = hs
        else:
            hspart = "_" * self.HASH_SIZE
        pattern = self.prefix + "-" + dtpart + "-" + hspart
        # 63 is max postgres db name, so we may truncate the hash part
        return pattern[:63]

    def _make_new_template_name(self, hashsum):
        return self._make_pattern(dt=datetime.utcnow(), hs=hashsum)

    def _create_db_from_template(self, dbname, template):
        _log.debug(f"Creating database {dbname} from {template}")
        self.cr.execute(
            f"""
            CREATE DATABASE "{dbname}"
            ENCODING 'unicode'
            TEMPLATE "{template}"
        """
        )

    def _rename_db(self, dbname_from, dbname_to):
        _log.debug(f"Renaming database {dbname_from} to {dbname_to}")
        self.cr.execute(
            f"""
            ALTER DATABASE "{dbname_from}"
            RENAME TO "{dbname_to}"
        """
        )

    def _drop_db(self, dbname):
        _log.debug(f"Dropping database {dbname}")
        self.cr.execute(
            f"""
            DROP DATABASE "{dbname}"
        """
        )

    def _find_template(self, hashsum):
        """ search same prefix and hashsum, any date """
        pattern = self.prefix + "-____________-" + hashsum
        self.cr.execute(
            """
            SELECT datname FROM pg_database
            WHERE datname like %s
            ORDER BY datname DESC  -- MRU first
        """,
            (pattern,),
        )
        r = self.cr.fetchone()
        if r:
            return r[0]
        else:
            return None

    def _touch(self, template_name, hashsum):
        # change the template date (MRU mechanism)
        assert template_name.endswith(hashsum)
        new_template_name = self._make_new_template_name(hashsum)
        if template_name != new_template_name:
            self._rename_db(template_name, new_template_name)

    def create(self, new_database, hashsum):
        """ Create a new database from a cached template matching hashsum """
        with self._lock():
            template_name = self._find_template(hashsum)
            if not template_name:
                return False
            else:
                self._create_db_from_template(new_database, template_name)
                self._touch(template_name, hashsum)
                return True

    def add(self, new_database, hashsum):
        """ Create a new cached template """
        with self._lock():
            template_name = self._find_template(hashsum)
            if template_name:
                self._touch(template_name, hashsum)
            else:
                new_template_name = self._make_new_template_name(hashsum)
                self._create_db_from_template(new_template_name, new_database)

    @property
    def size(self):
        with self._lock():
            pattern = self._make_pattern()
            self.cr.execute(
                """
                SELECT count(*) FROM pg_database
                WHERE datname like %s
            """,
                (pattern,),
            )
            return self.cr.fetchone()[0]

    def purge(self):
        with self._lock():
            pattern = self._make_pattern()
            self.cr.execute(
                """
                SELECT datname FROM pg_database
                WHERE datname like %s
            """,
                (pattern,),
            )
            for (datname,) in self.cr.fetchall():
                self._drop_db(datname)

    def trim_size(self, max_size):
        count = 0
        with self._lock():
            pattern = self._make_pattern()
            self.cr.execute(
                """
                SELECT datname FROM pg_database
                WHERE datname like %s
                ORDER BY datname DESC
                OFFSET %s
            """,
                (pattern, max_size),
            )
            for (datname,) in self.cr.fetchall():
                self._drop_db(datname)
                count += 1
        return count

    def trim_age(self, max_age):
        count = 0
        with self._lock():
            pattern = self._make_pattern()
            max_name = self._make_pattern(
                dt=datetime.utcnow() - max_age, hs=self.MAX_HASHSUM
            )
            self.cr.execute(
                """
                SELECT datname FROM pg_database
                WHERE datname like %s
                  AND datname <= %s
                ORDER BY datname DESC
            """,
                (pattern, max_name),
            )
            for (datname,) in self.cr.fetchall():
                self._drop_db(datname)
                count += 1
        return count

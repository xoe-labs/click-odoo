from datetime import datetime, timedelta

import dodoo_init.cache as cache

TEST_HASH_A = "a" * cache.DbCache.HASH_SIZE
TEST_HASH_B = "b" * cache.DbCache.HASH_SIZE
TEST_HASH_C = "c" * cache.DbCache.HASH_SIZE


def test_dbcache_create_purge(db, newdb, dbcache):
    assert dbcache.size == 0
    assert not dbcache.create(newdb, TEST_HASH_A)
    dbcache.add(db, TEST_HASH_A)
    assert dbcache.create(newdb, TEST_HASH_A)
    assert dbcache.size == 1
    dbcache.purge()
    assert dbcache.size == 0


def test_dbcache_create_touch(db, newdb, dbcache, mocker):
    assert dbcache.size == 0
    dt = mocker.patch("dodoo_init.cache.datetime")
    now = datetime.utcnow()
    dt.utcnow.return_value = now - timedelta(days=2)
    dbcache.add(db, TEST_HASH_A)
    dt.utcnow.return_value = now
    assert dbcache.create(newdb, TEST_HASH_A)
    assert dbcache.size == 1
    dbcache.trim_age(timedelta(days=1))
    assert dbcache.size == 1
    dbcache.purge()
    assert dbcache.size == 0


def test_dbcache_purge(db, dbcache):
    assert dbcache.size == 0
    dbcache.add(db, TEST_HASH_A)
    assert dbcache.size == 1
    dbcache.purge()
    assert dbcache.size == 0


def test_dbcache_trim_size(db, dbcache):
    assert dbcache.size == 0
    dbcache.add(db, TEST_HASH_A)
    assert dbcache.size == 1
    dbcache.add(db, TEST_HASH_B)
    assert dbcache.size == 2
    dbcache.add(db, TEST_HASH_C)
    assert dbcache.size == 3
    dbcache.trim_size(max_size=2)
    assert dbcache.size == 2
    dbcache.purge()
    assert dbcache.size == 0


def test_dbcache_trim_age(db, dbcache, mocker):
    assert dbcache.size == 0
    dt = mocker.patch("dodoo_init.cache.datetime")
    now = datetime.utcnow()
    dt.utcnow.return_value = now
    dbcache.add(db, TEST_HASH_A)
    assert dbcache.size == 1
    dt.utcnow.return_value = now - timedelta(days=2)
    dbcache.add(db, TEST_HASH_B)
    assert dbcache.size == 2
    dt.utcnow.return_value = now - timedelta(days=4)
    dbcache.add(db, TEST_HASH_C)
    assert dbcache.size == 3
    dt.utcnow.return_value = now
    dbcache.trim_age(timedelta(days=5))
    assert dbcache.size == 3
    dbcache.trim_age(timedelta(days=4))  # "older than 4"
    assert dbcache.size == 3
    dbcache.trim_age(timedelta(days=3))
    assert dbcache.size == 2
    dbcache.purge()
    assert dbcache.size == 0

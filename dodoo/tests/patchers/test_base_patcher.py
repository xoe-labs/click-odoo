import logging

import pytest

from dodoo.patchers import BasePatcher, PatchableProperty


class DummyPatchableProperty(PatchableProperty):
    def __init__(self, obj):
        self.obj = obj
        self.obj_path = obj.__name__

    def __get__(self, obj, type=None):
        return self.obj

    def __set__(self, obj, value):
        self.obj = value


class Dummy:
    pass


@pytest.fixture
def caplogd(caplog):
    caplog.set_level(logging.DEBUG)


@pytest.fixture
def Patchable():
    class Patchable:
        a = DummyPatchableProperty(Dummy)
        b = DummyPatchableProperty(Dummy)
        c = DummyPatchableProperty(Dummy)

    return Patchable


class TestPatcher:
    def test_patcher(self, Patchable, caplogd):
        class Patcher(Patchable, BasePatcher):
            @staticmethod
            def a():
                return "a"

            @classmethod
            def b(cls):
                return "b"

            def c(self):
                return "c"

        Patcher().apply()
        assert Patchable().a() == "a"
        assert Patchable().b() == "b"
        assert Patchable().c() == "c"

    def test_patcher_onfeature(self, Patchable, caplogd):
        class Patcher(Patchable, BasePatcher):
            @staticmethod
            @BasePatcher.onFeature("feat")
            def a():
                return "a"

            @classmethod
            @BasePatcher.onFeature("feat")
            def b(cls):
                return "b"

            @BasePatcher.onFeature("feat")
            def c(self):
                return "c"

        Patcher.features.update(feat=False)
        Patcher().apply()
        assert Patchable().a is Dummy
        assert Patchable().b is Dummy
        assert Patchable().c is Dummy

        Patcher.features.update(feat=True)
        Patcher().apply()
        assert Patchable().a() == "a"
        assert Patchable().b() == "b"
        assert Patchable().c() == "c"

    def test_patcher_unlessfeature(self, Patchable, caplogd):
        class Patcher(Patchable, BasePatcher):
            @staticmethod
            @BasePatcher.unlessFeature("feat")
            def a():
                return "a"

            @classmethod
            @BasePatcher.unlessFeature("feat")
            def b(cls):
                return "b"

            @BasePatcher.unlessFeature("feat")
            def c(self):
                return "c"

        Patcher.features.update(feat=True)
        Patcher().apply()
        assert Patchable().a is Dummy
        assert Patchable().b is Dummy
        assert Patchable().c is Dummy

        Patcher.features.update(feat=False)
        Patcher().apply()
        assert Patchable().a() == "a"
        assert Patchable().b() == "b"
        assert Patchable().c() == "c"


@pytest.fixture
def CustomList():
    class CustomList(list):
        pass

    return CustomList


class TestPatcherProperty:
    def test_patcher_property(self, Patchable, CustomList, caplogd):
        class Patcher(Patchable, BasePatcher):
            @property
            def a(self):
                return CustomList([])

        Patcher.features.update(feat=True)
        Patcher().apply()
        assert type(Patchable().a) is CustomList

    def test_patcher_property_onfeature(self, Patchable, CustomList, caplogd):
        class Patcher(Patchable, BasePatcher):
            @property
            @BasePatcher.onFeature("feat")
            def a(self):
                return CustomList([])

        Patcher.features.update(feat=False)
        Patcher().apply()
        assert Patchable().a is Dummy

        Patcher.features.update(feat=True)
        Patcher().apply()
        assert type(Patchable().a) is CustomList

    def test_patcher_property_unlessfeature(self, Patchable, CustomList, caplogd):
        class Patcher(Patchable, BasePatcher):
            @property
            @BasePatcher.unlessFeature("feat")
            def a(self):
                return CustomList([])

        Patcher.features.update(feat=True)
        Patcher().apply()
        assert Patchable().a is Dummy

        Patcher.features.update(feat=False)
        Patcher().apply()
        assert type(Patchable().a) is CustomList

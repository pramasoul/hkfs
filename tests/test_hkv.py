import pytest
import tempfile

from hkfs import FHK_CRD as HK

def test_exists():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        hk = HK(tmpdirname)

def test_create():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        hk = HK(tmpdirname)
        k1 = hk.create(b"foo")
        assert hk.exists(k1)
        assert hk.read(k1) == b"foo"
        k2 = hk.create(b"bar")
        assert k1 != k2
        assert hk.exists(k2)
        assert hk.read(k1) == b"foo"
        assert hk.read(k2) == b"bar"

import pytest
import tempfile

import hashlib
from random import shuffle
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

def test_create_otherhash():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        hk = HK(tmpdirname, hashfun = lambda x: hashlib.blake2b(x).digest())
        k1 = hk.create(b"foo")
        assert hk.exists(k1)
        assert hk.read(k1) == b"foo"
        k2 = hk.create(b"bar")
        assert k1 != k2
        assert hk.exists(k2)
        assert hk.read(k1) == b"foo"
        assert hk.read(k2) == b"bar"
        hk.delete(k1)
        assert not hk.exists(k1)

def test_create_many():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        hk = HK(tmpdirname, hashfun = lambda x: hashlib.blake2b(x).digest())
        expected_v_from_k = {}
        keys = set()
        for i in range(100):
            s = f"This is the {i}th string".encode('utf8')
            k = hk.create(s)
            assert k not in keys
            keys.add(k)
            expected_v_from_k[k] = s
        for k in keys:
            assert hk.read(k) == expected_v_from_k[k]
            hk.delete(k)

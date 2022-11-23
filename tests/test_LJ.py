import pytest

import os
import stat
import tempfile

from base64 import urlsafe_b64decode
from blake3 import blake3
from pathlib import Path

from lj import LJ

def test_LJ_create():
    # create an LJ
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        lj = LJ(tmpdirname)

def test_LJ_key_from_file():
    from base64 import urlsafe_b64decode
    # get a hash key from a file contents
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        lj = LJ(tmpdirname)
        with tempfile.NamedTemporaryFile(dir=tmpdirname) as f1:
            f1.write(b"foobar\n")
            f1.seek(0)
            k = lj.key_from_file(f1)
            assert len(k) == 32
            # verify equal to result of echo foobar | b3sum
            assert urlsafe_b64decode(lj._encode_key(k) + '==').hex() == \
                "534659321d2eea6b13aea4f4c94c3b4f624622295da31506722b47a8eb9d726c"
            # find the directory and path from the key
            directory, path = lj._dir_and_path_from_key(k)
            assert str(directory).startswith(tmpdirname)
            assert str(path).startswith(str(directory))
            assert urlsafe_b64decode(path.name + '==') == k

def test_LJ_assimilate():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as hashdirname:
        lj = LJ(hashdirname)
        with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
            with tempfile.NamedTemporaryFile(dir=tmpdirname) as f1:
                f1.write(b"foo")
                f1.seek(0)
                k1 = lj.key_from_file(f1)
                f1.seek(0)
                with tempfile.NamedTemporaryFile(dir=tmpdirname) as f2:
                    f2.write(b"bar")
                    f2.seek(0)
                    k2 = lj.key_from_file(f2)
                    f2.seek(0)
                    with tempfile.NamedTemporaryFile(dir=tmpdirname) as f3:
                        f3.write(b"foo")
                        f3.seek(0)
                        k3 = lj.key_from_file(f3)
                        f3.seek(0)
                        assert k1 == k3
                        assert k1 != k2
                        assert len(os.listdir(hashdirname)) == 0
                        assert sorted(os.path.join(tmpdirname, n) for n in os.listdir(tmpdirname)) \
                            == sorted([f1.name, f2.name, f3.name])
                        assert lj.assimilate(f1) == "added"
                        assert len(os.listdir(hashdirname)) == 1
                        assert sorted(os.path.join(tmpdirname, n) for n in os.listdir(tmpdirname)) \
                            == sorted([f1.name, f2.name, f3.name])
                        assert lj.assimilate(f2) == "added"
                        assert len(os.listdir(hashdirname)) == 2
                        assert sorted(os.path.join(tmpdirname, n) for n in os.listdir(tmpdirname)) \
                            == sorted([f1.name, f2.name, f3.name])
                        assert lj.assimilate(f3) == "linked"
                        assert len(os.listdir(hashdirname)) == 2
                        assert sorted(os.path.join(tmpdirname, n) for n in os.listdir(tmpdirname)) \
                            == sorted([f1.name, f2.name, f3.name])
                    
def test_LJ_assimilate_2():
    contents_by_filename = {"t.1": "foo", "t.2": "bar", "t.3": "foo"}
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as hashdirname:
        lj = LJ(hashdirname)
        with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
            # create test files
            for fname, contents in contents_by_filename.items():
                with open(os.path.join(tmpdirname, fname), 'w') as f:
                    f.write(contents)
            assert len(os.listdir(hashdirname)) == 0
            assert sorted(os.listdir(tmpdirname)) == sorted(contents_by_filename.keys())

            # Assimilate one-by-one and check at each step

            with open(os.path.join(tmpdirname, "t.1"), 'rb') as f:
                assert lj.assimilate(f) == "added"
            assert len(os.listdir(hashdirname)) == 1
            assert sorted(os.listdir(tmpdirname)) == sorted(contents_by_filename.keys())

            with open(os.path.join(tmpdirname, "t.2"), 'rb') as f:
                assert lj.assimilate(f) == "added"
            assert len(os.listdir(hashdirname)) == 2
            assert sorted(os.listdir(tmpdirname)) == sorted(contents_by_filename.keys())

            with open(os.path.join(tmpdirname, "t.3"), 'rb') as f:
                assert lj.assimilate(f) == "linked"
            assert len(os.listdir(hashdirname)) == 2
            assert sorted(os.listdir(tmpdirname)) == sorted(contents_by_filename.keys())


def test_LJ_assimilate_with_key():
    contents_by_filename = {"t.1": "foo", "t.2": "bar", "t.3": "foo"}
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as hashdirname:
        lj = LJ(hashdirname)
        with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
            # create test files
            for fname, contents in contents_by_filename.items():
                with open(os.path.join(tmpdirname, fname), 'w') as f:
                    f.write(contents)
            assert len(os.listdir(hashdirname)) == 0
            assert sorted(os.listdir(tmpdirname)) == sorted(contents_by_filename.keys())

            # Assimilate one-by-one and check keys

            with open(os.path.join(tmpdirname, "t.1"), 'rb') as f:
                # verify equal to result of echo -n foo | b3sum
                assert lj.assimilate_tell_key(f).hex() == \
                    "04e0bb39f30b1a3feb89f536c93be15055482df748674b00d26e5a75777702e9"

            with open(os.path.join(tmpdirname, "t.2"), 'rb') as f:
                # verify equal to result of echo -n bar | b3sum
                assert lj.assimilate_tell_key(f).hex() == \
                    "f2e897eed7d206cd855d441598fa521abc75aa96953e97c030c9612c30c1293d"

            with open(os.path.join(tmpdirname, "t.3"), 'rb') as f:
                # verify equal to result of echo -n foo | b3sum
                assert lj.assimilate_tell_key(f).hex() == \
                    "04e0bb39f30b1a3feb89f536c93be15055482df748674b00d26e5a75777702e9"
                    

import pytest

import os
import stat
import tempfile

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
    from base64 import urlsafe_b64decode
    # get a hash key from a file contents
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        lj = LJ(tmpdirname)
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
                    assert lj.assimilate(f1) == "added"
                    assert lj.assimilate(f2) == "added"
                    assert lj.assimilate(f3) == "linked"
                    
                    

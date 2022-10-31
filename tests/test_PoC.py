import pytest

import os
import stat
import tempfile

from pathlib import Path

def test_mktmps():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        status = os.lstat(tmpdirname)
        assert stat.S_ISDIR(status.st_mode)
        with tempfile.NamedTemporaryFile(dir=tmpdirname) as f1:
            assert stat.S_ISREG(os.lstat(f1.name).st_mode)
            with tempfile.NamedTemporaryFile(dir=tmpdirname) as f2:
                assert stat.S_ISREG(os.lstat(f2.name).st_mode)
                assert f1.name != f2.name

def test_mktmps_pathlib():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        dpath = Path(tmpdirname)
        assert dpath.is_dir()
        with tempfile.NamedTemporaryFile(dir=tmpdirname) as f1:
            f1_basename = Path(f1.name).name
            assert (dpath / Path(f1.name)).is_file() # MYSTERY: why does this work?
            assert (dpath / f1_basename).is_file()
            with tempfile.NamedTemporaryFile(dir=tmpdirname) as f2:
                f2_basename = Path(f2.name).name
                assert (dpath / f2_basename).is_file()
                assert f1_basename != f2_basename


def test_mktmps_pathlib_dir_fd():
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        dpath = Path(tmpdirname)
        assert dpath.is_dir()
        dir_fd = os.open(tmpdirname, os.O_RDONLY)
        with tempfile.NamedTemporaryFile(dir=tmpdirname) as f1:
            f1_basename = Path(f1.name).name
            assert stat.S_ISREG(os.lstat(f1_basename, dir_fd=dir_fd).st_mode)
            with tempfile.NamedTemporaryFile(dir=tmpdirname) as f2:
                f2_basename = Path(f2.name).name
                assert stat.S_ISREG(os.lstat(f2_basename, dir_fd=dir_fd).st_mode)
                assert f1_basename != f2_basename

        os.close(dir_fd)


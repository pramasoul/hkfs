import pytest

import os
import stat
import tempfile

from pathlib import Path

def test_mktmps():
    # Make a tmp directory containing two tmp files
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        status = os.lstat(tmpdirname)
        assert stat.S_ISDIR(status.st_mode)
        with tempfile.NamedTemporaryFile(dir=tmpdirname) as f1:
            assert stat.S_ISREG(os.lstat(f1.name).st_mode)
            with tempfile.NamedTemporaryFile(dir=tmpdirname) as f2:
                assert stat.S_ISREG(os.lstat(f2.name).st_mode)
                assert f1.name != f2.name

def test_mktmps_pathlib():
    # Make a tmp directory containing two tmp files, using pathlib
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
    # Make a tmp directory containing two tmp files, using a dir_fd directory reference
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

def test_link():
    # Make a hard link
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        dpath = Path(tmpdirname)
        assert dpath.is_dir()
        dir_fd = os.open(tmpdirname, os.O_RDONLY)
        os.mknod("t.1", dir_fd=dir_fd)
        os.mknod("t.2", dir_fd=dir_fd)
        assert sorted(os.listdir(dpath)) == ["t.1", "t.2"]
        sr1 = os.lstat("t.1", dir_fd=dir_fd)
        sr2 = os.lstat("t.2", dir_fd=dir_fd)
        assert stat.S_ISREG(sr1.st_mode)
        assert stat.S_ISREG(sr2.st_mode)
        assert sr1.st_nlink == 1
        assert sr2.st_nlink == 1
        assert sr1.st_ino != sr2.st_ino
        os.remove("t.2", dir_fd=dir_fd)
        with pytest.raises(FileNotFoundError):
            sr2 = os.lstat("t.2", dir_fd=dir_fd)
        assert sorted(os.listdir(dpath)) == ["t.1"]
        os.link("t.1", "t.2", src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        sr1 = os.lstat("t.1", dir_fd=dir_fd)
        sr2 = os.lstat("t.2", dir_fd=dir_fd)
        assert sr1.st_ino == sr2.st_ino
        assert sr1.st_nlink == sr2.st_nlink == 2
        assert sorted(os.listdir(dpath)) == ["t.1", "t.2"]
        os.close(dir_fd)

def test_link_2():
    # Make a hard link to a file and verify contents
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        dpath = Path(tmpdirname)
        assert dpath.is_dir()
        dir_fd = os.open(tmpdirname, os.O_RDONLY)
        with open(dpath / "t.1", 'w') as f:
            f.write("This is t.1\n")
        sr1 = os.lstat("t.1", dir_fd=dir_fd)
        assert stat.S_ISREG(sr1.st_mode)
        assert sr1.st_nlink == 1
        os.link("t.1", "t.2", src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        sr1 = os.lstat("t.1", dir_fd=dir_fd)
        sr2 = os.lstat("t.2", dir_fd=dir_fd)
        assert sr1.st_ino == sr2.st_ino
        assert sr1.st_nlink == sr2.st_nlink == 2
        assert sorted(os.listdir(dpath)) == ["t.1", "t.2"]
        with open(dpath / "t.2") as f:
            assert f.read() == "This is t.1\n"
        os.close(dir_fd)

def test_link_ro():
    # If one of two hard-linked files is read-only, what is enforced?
    # Answer: they're all then read-only
    with tempfile.TemporaryDirectory(prefix="/roto/tmp/") as tmpdirname:
        dpath = Path(tmpdirname)
        dir_fd = os.open(tmpdirname, os.O_RDONLY)
        with open(dpath / "t.1", 'w') as f:
            f.write("This is t.1\n")
        sr1 = os.lstat("t.1", dir_fd=dir_fd)
        assert stat.S_ISREG(sr1.st_mode)
        assert sr1.st_nlink == 1
        os.link("t.1", "t.2", src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        with open(dpath / "t.2") as f:
            assert f.read() == "This is t.1\n"
        os.chmod("t.2", stat.S_IREAD, dir_fd=dir_fd)
        with pytest.raises(PermissionError):
            with open(dpath / "t.1", 'w') as f:
                f.write("This is an attempted write of the writeable file\n")
        with open(dpath / "t.2") as f:
            assert f.read() == "This is t.1\n"
        # This is because there's only one file, and the inode holds all but the namne:
        assert os.lstat("t.1", dir_fd=dir_fd) == os.lstat("t.2", dir_fd=dir_fd)
        os.chmod("t.2", stat.S_IREAD | stat.S_IWRITE, dir_fd=dir_fd)
        with open(dpath / "t.1", 'w') as f:
            f.write("This is an attempted write of the writeable file\n")
        with open(dpath / "t.2") as f:
            assert f.read() == "This is an attempted write of the writeable file\n"

        os.close(dir_fd)


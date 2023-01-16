# link juggler

import os

from base64 import urlsafe_b64encode
from blake3 import blake3
from pathlib import Path


class LJ():
    def __init__(self, directory, post_assimilation=lambda name, sk: True):
        self.d = Path(directory)
        #self.dh = os.open(str(Path(directory)), os.O_RDONLY)
        self.post_assimilation = post_assimilation
        self.h = blake3
        self.buf_len = 1<<20

    def _assimilate(self, f):
        key = self.key_from_file(f)
        hashdir_path, hashfile_path = self._dir_and_path_from_key(key)
        real_f_path = os.path.realpath(f.name) # FIXME: is this necessary?
        hashfile_path_str = str(hashfile_path)
        if hashfile_path.exists():
            # replace f with link
            # TODO: make safer
            os.remove(f.name)
            os.link(hashfile_path_str, real_f_path)
            what = "linked"
        else:
            hashdir_path.mkdir(parents=True, exist_ok=True)
            # link f into hash pile
            os.link(f.name, str(hashfile_path))
            #return f"linked {f.name} to {hashfile_path}"
            what = "added"
        status = os.lstat(hashfile_path_str)
        inode = status.st_ino
        return what, key, inode

    def assimilate(self, f):
        return self._assimilate(f)[0]

    def assimilate_tell_key(self, f):
        return self._assimilate(f)[1]

    def exists(self, key):
        return self._path_from_key(key).exists()

    def key_from_file(self, f):
        hasher = self.h()
        buf = f.read(self.buf_len)
        while buf:
            hasher.update(buf)
            buf = f.read(self.buf_len)
        return hasher.digest()

    def _encode_key(self, kb):
        return urlsafe_b64encode(kb).rstrip(b'=').decode('ascii')

    def _dir_and_path_from_key(self, key):
        # Here is where the file system structure is determined for the KV store
        assert(len(key) >= 4)
        encoded_key = self._encode_key(key)
        directory = self.d / encoded_key[:2] / encoded_key[2:4]
        #directory = os.path.join(encoded_key[:2], encoded_key[2:4])
        #return directory, os.path.join(directory, encoded_key)
        return directory, directory / encoded_key

    def _path_from_key(self, key):
        _, rv = self._dir_and_path_from_key(key)
        return rv

    def assimilate_tree(self, dirname):
        paf = self.post_assimilation
        for root, dirs, files in os.walk(dirname):
            directory = Path(root)
            for name in files:
                with open(directory / name, 'rb') as f:
                    paf(name, self._assimilate(f))

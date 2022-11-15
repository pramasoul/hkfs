# link juggler

import os

from base64 import urlsafe_b64encode
from blake3 import blake3
from pathlib import Path


class LJ():
    def __init__(self, directory):
        self.d = Path(directory)
        #self.dh = os.open(str(Path(directory)), os.O_RDONLY)
        self.h = blake3
        self.buf_len = 1<<20

    def assimilate(self, f):
        key = self.key_from_file(f)
        dir_path, file_path = self._dir_and_path_from_key(key)
        f_path = os.path.realpath(f.name)
        if file_path.exists():
            # replace f with link
            # TODO: make safer
            os.remove(f.name)
            os.link(str(file_path), f_path)
            return "linked"
        dir_path.mkdir(parents=True, exist_ok=True)
        # link f into hash pile
        os.link(f.name, str(file_path))
        #return f"linked {f.name} to {file_path}"
        return "added"


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

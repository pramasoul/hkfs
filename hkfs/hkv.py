# ## Hash-Key Create Read Delete
# * The contents upon creation determine the key.
# ** Create from data, or from file
# ** Creation returns the key
# * Range reads allowed
# * Contents are immutable
# * Can delete but not alter

import os

# In[12]:


class HK_CRD():
    def __init__(self):
        pass
    
    def exists(self, key):
        raise NotImplementedError
        
    def key(self, data):
        raise NotImplementedError
        
    def key_from_file(self, file):
        raise NotImplementedError
        
    def create(self, data):
        raise NotImplementedError

    def create_from_file(self, file):
        raise NotImplementedError
        
    def read(self, key, offset, len):
        raise NotImplementedError
        
    def delete(self, key):
        raise NotImplementedError


# In[13]:


from base64 import urlsafe_b64encode
from pathlib import Path
import hashlib

class FHK_CRD(HK_CRD):
    def __init__(self, dir, hashfun=None):
        self.d = Path(dir)
        if hashfun:
            self.hashfun = hashfun
        else:
            self.hashfun = lambda x: hashlib.sha256(x).digest()
        self.max_read_len = 1<<31
        #self.d.mkdir(parents=True, exist_ok=True)
        # ^^^ No, require the directory already to exist
        self.buf_len = 1<<20
        
    def key(self, data):
        return self.hashfun(data)

    # This doesn't really work with arbitrary hashfun
    def key_from_file(f, file):
        file.seek(0,0)
        h = self.hashfun
        b = file.read(self.buf_len)
        while b:
            h.update(b)
            b = file.read(self.buf_len)
        return h.digest()
    
    def _encode_key(self, kb):
        return urlsafe_b64encode(kb).rstrip(b'=').decode('ascii')
    
    def create(self, data):
        key = self.key(data)
        dir_path, file_path = self._dir_and_path_from_key(key)
        dir_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(data)
        return key
            
    def exists(self, key):
        return self._path_from_key(key).exists()
    
    def _dir_and_path_from_key(self, key):
        # Here is where the file system structure is determined for the KV store
        assert(len(key) >= 4)
        encoded_key = self._encode_key(key)
        dir = self.d / encoded_key[:2] / encoded_key[2:4]
        return dir, dir / encoded_key
        
    def _path_from_key(self, key):
        _, rv = self._dir_and_path_from_key(key)
        return rv
    
    def read(self, key, offset=0, len=1<<31):
        _, file_path = self._dir_and_path_from_key(key)
        with open(file_path, 'rb') as f:
            f.seek(offset)
            rv = f.read(len)
        return rv

    def delete(self, key):
        _, file_path = self._dir_and_path_from_key(key)
        os.remove(file_path)

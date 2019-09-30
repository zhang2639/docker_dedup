from CodernityDB.database import Database
from CodernityDB.hash_index import HashIndex

from db.datastore import DataStore


class WithXIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = 'I'
        super(WithXIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        a_val = data.get("x")
        if a_val is not None:
            return a_val, None
        return None

    def make_key(self, key):
        return key


class CodernityStore(DataStore):

    def __init__(self, redis_server_ip):
        self.db = Database('/tmp/db_a')
        self.db.create()
        x_ind = WithXIndex(self.db.path, 'x')
        self.db.add_index(x_ind)

    def put(self, key, value):
        self.db.insert(dict(x=key, chunk=value))

    def get(self, key):
        return self.db.get('x', key, with_doc=True)['doc']['chunk']

    def exists(self, key):
        return self.r.exists(key)

    def persist(self):
        pass

    def close(self):
        pass

    def used_memory(self):
        return 0

    def dump(self):
        return "dbsize: %d \n info: %r" % (0, 0)

    def reset(self):
        pass

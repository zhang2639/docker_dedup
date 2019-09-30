import sqlite3

from db.datastore import DataStore


class SQLiteStore(DataStore):

    def __init__(self, db_name):
        self._conn = sqlite3.connect(db_name, check_same_thread=False)
        self._conn.isolation_level = None
        self._conn.text_factory = str

        self.commit_count = 0

        import os
        if os.path.isfile(db_name): # db already exist
            cursor = self._conn.cursor()
            digest = cursor.execute('SELECT digest FROM chunk').fetchall()
            self._mem_key = set(map(lambda x: x[0], digest)) # read keys
        else:
            self._mem_key = set()

            cursor = self._conn.cursor()
            cursor.execute('''CREATE TABLE chunk(digest text PRIMARY KEY, bblock)''')
            self._conn.commit()

    def put(self, key, value):
        if self.exist(key):
            return
        self._mem_key.add(key)
        cursor = self._conn.cursor()
        cursor.execute("insert into chunk values (?, ?)", (key, value))
        self.commit_count += 1
        if self.commit_count == 10**4:
            self.commit_count = 0
            self._conn.commit()

    def get(self, key):
        cursor = self._conn.cursor()
        cursor.execute("select bblock from chunk where digest=:digest", {"digest": key})
        return cursor.fetchone()[0]

    def exists(self, key):
        return key in self._mem_key

    def persist(self):
        self._conn.commit()

    def close(self):
        self._conn.commit()
        self._conn.close()

    def dump(self):
        s = "Number of keys: %d\n" % len(self._mem_key)
        for line in self._conn.iterdump():
            if line.startswith('INSERT INTO "chunk"'):
                s += '%s\n' % line
        return s

    def reset(self):
        cursor = self._conn.cursor()
        cursor.execute("delete from chunk")
        self._mem_key = set()

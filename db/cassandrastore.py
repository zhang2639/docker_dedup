from cassandra.cluster import Cluster

from db.datastore import DataStore


class CassandraStore(DataStore):

    def __init__(self, cassandra_server_ip):
        cluster = Cluster([cassandra_server_ip])

        tries = 0
        while True:
            try:
                session = cluster.connect()
                break
            except Exception as e:
                print "e:", e
                print "cassandra-server isn't ready yet.."
                import time
                time.sleep(5)
                cluster = Cluster([cassandra_server_ip])
                tries += 1
                if tries == 5:
                    raise e

        print "successfully connected to cassandra-server"

        try:
            session.execute("CREATE KEYSPACE tp WITH replication = "
                            "{'class':'SimpleStrategy','replication_factor':1}")
        except Exception as e:
            pass

        session.set_keyspace('tp')
        # session.execute("use tp")
        # session.execute("CONSISTENCY ONE")
        # print "default_consistency_level: (10)", session.default_consistency_level

        try:
            query = """CREATE TABLE chunk(digest text PRIMARY KEY, block blob)
                    WITH caching = {'keys':'ALL', 'rows_per_partition':'1000'}"""
            session.execute(query)
        except Exception as e:
            pass
        try:
            session.execute("TRUNCATE chunk")
        except Exception as e:
            pass

        self.insert_stmt = session.prepare("INSERT INTO chunk (digest, block) VALUES(?, ?)")
        self.lookup_stmt = session.prepare("SELECT * FROM chunk WHERE digest=?")

        self.session = session

    def put(self, key, value):
        self.session.execute(self.insert_stmt, (key, value))

    def get(self, key):
        result = self.session.execute(self.lookup_stmt, (key, ))
        return list(result)[0].block

    def exists(self, key):
        result = self.session.execute(self.lookup_stmt, (key, ))
        return len(list(result)) > 0

    def dbsize(self):
        return len(list(self.session.execute("SELECT * FROM chunk")))

    def persist(self):
        pass

    def close(self):
        pass

    def used_memory(self):
        return 0

    def dump(self):
        return "dbsize: %d \n info: -" % (int(self.dbsize()), )

    def reset(self):
        self.session.execute("TRUNCATE chunk")


class CassandraStore_use_image_type(DataStore):

    def __init__(self, cassandra_server_ip):
        cluster = Cluster([cassandra_server_ip])

        tries = 0
        while True:
            try:
                session = cluster.connect()
                break
            except Exception as e:
                print "e:", e
                print "cassandra-server isn't ready yet.."
                import time
                time.sleep(5)
                cluster = Cluster([cassandra_server_ip])
                tries += 1
                if tries == 5:
                    raise e

        print "successfully connected to cassandra-server"

        try:
            session.execute("CREATE KEYSPACE tp WITH replication = "
                            "{'class':'SimpleStrategy','replication_factor':1}")
        except Exception as e:
            pass

        session.set_keyspace('tp')
        # session.execute("use tp")
        # session.execute("CONSISTENCY ONE")
        # print "default_consistency_level: (10)", session.default_consistency_level

        try:
            query = """CREATE TABLE chunk(digest text PRIMARY KEY, block blob)
                    WITH caching = {'keys':'ALL', 'rows_per_partition':'1000'}"""
            session.execute(query)
        except Exception as e:
            pass
        try:
            session.execute("TRUNCATE chunk")
        except Exception as e:
            pass

        self.insert_stmt = session.prepare("INSERT INTO chunk (digest, block) VALUES(?, ?)")
        self.lookup_stmt = session.prepare("SELECT * FROM chunk WHERE digest=?")

        self.session = session

    def put(self, key, value):
        self.session.execute(self.insert_stmt, (key, value))

    def get(self, key):
        result = self.session.execute(self.lookup_stmt, (key, ))
        return list(result)[0].block

    def exists(self, key):
        result = self.session.execute(self.lookup_stmt, (key, ))
        return len(list(result)) > 0

    def dbsize(self):
        return len(list(self.session.execute("SELECT * FROM chunk")))

    def persist(self):
        pass

    def close(self):
        pass

    def used_memory(self):
        return 0

    def dump(self):
        return "dbsize: %d \n info: -" % (int(self.dbsize()), )

    def reset(self):
        self.session.execute("TRUNCATE chunk")

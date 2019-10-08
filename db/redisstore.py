import redis

from db.datastore import DataStore


class RedisStore(DataStore):

    def __init__(self, redis_server_ip):
        pool = redis.ConnectionPool(host=redis_server_ip, port=6379, db=0)
        self.r = redis.StrictRedis(connection_pool=pool)

    def put(self, key, value):
        self.r.set(key, value)

    def get(self, key):
        return self.r.get(key)

    def exists(self, key):
        return self.r.exists(key)

    def ladd(self, list_key, value):
        self.r.lpush(list_key, value)

    def lget(self, list_key):
        return self.r.lrange(list_key, 0, -1)

    def llen(self, list_key):
        return self.r.llen(list_key)

    def persist(self):
        pass

    def close(self):
        pass

    def used_memory(self):
        return self.r.info()['used_memory']

    def dump(self):
        #return "dbsize: %d \n info: %r\nmemmory:%s  memmory_dataset:%s" % (int(self.r.dbsize()), self.r.info(), self.r.info()['used_memory_human'], self.r.info()['used_memory_dataset'])
	return "dbsize: %d \n info: %r\nmemmory:%s" % (int(self.r.dbsize()), self.r.info(), self.r.info()['used_memory_human'])

    def reset(self):
        self.r.flushall()

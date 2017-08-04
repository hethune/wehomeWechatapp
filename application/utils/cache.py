"""
This is a redis cache like LruCache
use the db 1
"""
import redis
class RedisCache(list):

    def __init__(self, host, port, password, dbname, db=1):

        list.__init__([])
        self.dbname = dbname
        self.client = redis.Redis(host=host, port=port, password=password,db=db)

    def __getitem__(self, key):
        '''
        if the key exists then return the cache data
        else return None
        '''
        hexists = self.client.hexists(self.dbname, key)
        if hexists :
            return self.client.hget(self.dbname, key).decode("utf-8")
        else:
            return None

    def __setitem__(self, key, value):
        self.client.hset(self.dbname, key, value)
        return value

    def remove_all(self):
        assert self.dbname is not None, 'dbname is None'
        self.client.delete(self.dbname)

class HomeCache(list):

    def __init__(self, host, port, password, db=1):

        list.__init__([])
        self.client = redis.Redis(host=host, port=port, password=password, db=db)

    def __getitem__(self, key):
        '''
        if the key exists then return the cache data
        else return None
        '''
        exists = self.client.exists(name=key)
        if exists :
            return self.client.get(name=key).decode("utf-8")
        else:
            return None

    def __setitem__(self, key, value):
        self.client.set(key, value)
        return value

    def set_key_value(self, name, value, expiration):
        self.client.set(name=name, value=value)
        self.client.expire(name=name, time=expiration)
        return value
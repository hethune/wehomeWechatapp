import redis

class RedisDB(object):

  def __init__(self, host, port, dbname, db):
    self.dbname = dbname
    self.client = redis.StrictRedis(host=host, port=port, db=db)

  def get(self, key):
    '''
    if the key exists then return the cache data
    else return None
    '''
    hexists = self.client.hexists(self.dbname, key)
    if hexists :
      return self.client.hget(self.dbname, key)
    else:
      return None

  def set(self, key, value):
    self.client.hset(self.dbname, key, value)
    return value

  def pure_set(self, key, value):
    return self.client.set(key, value)

  def pure_get(self, key):
    return self.client.get(key)

  def expire(self, key, time):
    return self.client.expire(key, time)

  def lpush(self, key, value):
    return self.client.lpush(key, value)

  def lrem(self, key, value):
    return self.client.lrem(key, 0, value)

  def lrange(self, key, range):
    return self.client.lrange(key, 0, range)

  def sadd(self, key, value):
    return self.client.sadd(key, value)

  def srem(self, key, value):
    return self.client.srem(key, value)

  def smembers(self, key):
    return self.client.smembers(key)

  def incr(self, key):
    self.client.hincrby(self.dbname, key, 1)

  def pure_incr(self, key):
    self.client.incr(key)

  def decr(self, key):
    self.client.hincrby(self.dbname, key, -1)

  def remove_all(self):
    assert self.dbname is not None, 'dbname is None'
    self.client.delete(self.dbname)

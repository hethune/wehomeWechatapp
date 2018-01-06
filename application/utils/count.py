class Count(object):
  VISIT_ACTION = 1

  PROPERTY_TYPE = 1
  CITY_TYPE = 2
  LISTING_TYPE = 3
  AUTOCOMPLETE_TYPE = 4

  TYPE_MAP = {
    1: "property_api",
    2: "city_api",
    3: "list_api",
    4: "auto_complete"
  }

  ACTION_MAP = {
    1: "visit",
  }

  def __init__(self, redis_db):
    self.redis_db = redis_db

  def get(self, company, action, content_type):
    '''
    if the key exists then return the cache data
    else return None
    '''
    key = self.generate_key(company, action, content_type)
    return self.redis_db.get(key)

  def incr(self, company, action, content_type):
    key = self.generate_key(company, action, content_type)
    return self.redis_db.incr(key)

  def decr(self, company, action, content_type):
    key = self.generate_key(company, action, content_type)
    return self.redis_db.decr(key)

  @classmethod
  def generate_key(cls, company, action, content_type):
    key = "{}_{}_{}".format(company, cls.ACTION_MAP[action], cls.TYPE_MAP[content_type])
    return key

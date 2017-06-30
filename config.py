class BaseConfig(object):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://wehome:wehome@127.0.0.1/wehome"
  SQLALCHEMY_TRACK_MODIFICATIONS = True
  WECHAT_TOKEN = 'LGB4XFIOg2LRWni3KQsNKxNV6o0WJndA'
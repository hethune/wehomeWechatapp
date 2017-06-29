class BaseConfig(object):
  DEBUG = True
  # SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:123456abc@localhost/wehometest"
  SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://wehome:wehome@127.0.0.1/wehome"
  SQLALCHEMY_TRACK_MODIFICATIONS = True
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from config import BaseConfig
import logging
app = Flask(__name__)
app.config.from_object(BaseConfig)
app.secret_key = app.config['APP_SECRET_KEY']
db = SQLAlchemy(app)
# logger

class RequestIdFilter(logging.Filter):
  # This is a logging filter that makes the request ID available for use in
  # the logging format. Note that we're checking if we're in a request
  # context, as we may want to log things before Flask is fully loaded.
  def filter(self, record):
    record.request_id = g.get("uuid")
    return True

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(request_id)s %(message)s'))
app.logger.addHandler(handler)
app.logger.addFilter(RequestIdFilter())
app.logger.handlers.extend(logging.getLogger("wehomeWechatapp.log").handlers)
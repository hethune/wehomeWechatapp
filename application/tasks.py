from index import celery
from utils.comm import Notification

@celery.task(name="tasks.notification")
def send_sms_mobilecode(mobile, country, code):
  return Notification.send_sms_message(mobile, country, 0, code)
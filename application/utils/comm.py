# -*- coding: utf-8 -*-

# Yunpian sms
# ToDo: make this async
import httplib
import urllib
import json
import requests

from index import app
from ..template import message_list

class Notification(object):

  @classmethod
  def gen_sms_phone_code_message(cls, **kwargs):
    text_type = kwargs.get('text_type', None)
    return message_list[str(kwargs.get('country', None))][text_type]

  @classmethod
  def send_sms_cn(cls, **kwargs):
    text = cls.gen_sms_phone_code_message(**kwargs).format(kwargs.get('text', None))
    apikey = app.config['YUNPIAN_KEY']
    sms_host = "sms.yunpian.com"
    port = 443
    version = "v2"
    sms_send_uri = "/" + version + "/sms/single_send.json"
    params = urllib.urlencode({'apikey': apikey, 'text': text, 'mobile': kwargs.get('mobile', None)})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    conn = httplib.HTTPSConnection(sms_host, port=port, timeout=30)
    response_json = {}
    try:
      conn.request("POST", sms_send_uri, params, headers)
      response = conn.getresponse()
      response_json = json.loads(response.read())
    finally:
      conn.close()
    success = response_json.get("code") == 0
    if not success:
      app.logger.error("Failed to send sms code to {} {}".format(kwargs.get('mobile', None), response_json))
    return success

  @classmethod
  def send_sms_message(cls, mobile, country, text_type, text):
    status = False
    if app.config['TESTING']:
      return True
    if country == "86":
      status = cls.send_sms_cn(mobile=mobile, country=country, text_type=int(text_type), text=text)
    elif country == "1":
      status = cls.send_sms_nexmo(mobile=mobile, country=country, text_type=int(text_type), text=text)
    else:
      app.logger.warn("country code not supported {} {}".format(country, mobile))
    return status


  @classmethod
  def send_sms_nexmo(cls, **kwargs):
    print kwargs
    text = cls.gen_sms_phone_code_message(**kwargs).format(kwargs.get('text', None))
    params = {
      'api_key': app.config.get("NEXMO_KEY"),
      'api_secret': app.config.get("NEXMO_SECRET"),
      'to': "{}{}".format(kwargs.get('country', None), kwargs.get('mobile', None)),
      'from': "18889706966",
      'text' : text
    }
    r = requests.get('https://rest.nexmo.com/sms/json', params=params)
    success = False
    if r.status_code == 200:
      response_json = r.json()
      if len(response_json["messages"]) > 0 and response_json["messages"][0]["status"] == "0":
        success = True
    if not success:
      app.logger.error("Failed to send nexmo sms to {}, response is {}".format(kwargs.get('mobile', None), r))
    return success
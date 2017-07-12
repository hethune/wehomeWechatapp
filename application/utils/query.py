from ..models import City, IndexPage, CityPage, HomePage, UnmatchedPlace, FeedBack, User, Phone
from index import app, db
from flask import jsonify
from sqlalchemy import and_
import hashlib
from urllib import quote_plus
import requests
import json

class QueryHelper(object):
  'You can use this class query the complex query via the SqlAlchemy query'
  @classmethod
  def to_json_with_filter(cls, rows_dict, columns):
    d = {'success':True}
    for k, v in rows_dict.items():
      # handle the dict and integer and float
      if type(v) == type({}) or type(v) == type(1) or type(v) == type(1.0) or type(v) == type('') or type(v) == type(u''):
        d[k] = v
      # handle the model object
      elif (type(v) != type([])) and (v is not None):
        d[k] = {_k:_v for _k, _v in v.__dict__.items() if _k in columns}
      # handle the list
      elif v is not None:
        l = []
        for item in v:
          # handle the model object
          if type(item) != type({}):
            l.append({_k:_v for _k, _v in item.__dict__.items() if _k in columns})
          # handle the dict  
          else:
            l.append({_k:_v for _k, _v in item.items() if _k in columns})
        d[k] = l
      # handle the None  
      else:
        d[k] = {}
    return jsonify(d), 200

  @classmethod
  def get_index_page(cls):
    return IndexPage.query.first()

  @classmethod
  def get_cities(cls):
    return City.query.all()

  @classmethod
  def get_city_page_with_city_id(cls, city_id):
    return CityPage.query.filter_by(city_id=city_id).first()

  @classmethod
  def get_home_page_with_home_id(cls, home_id):
    return HomePage.query.filter_by(id=home_id).first()

  @classmethod
  def get_home_page_with_place_name(cls, place_name):
    md5 = hashlib.md5()
    md5.update(place_name.encode("utf-8"))
    return HomePage.query.filter(and_(HomePage.hash_code==md5.hexdigest(), HomePage.map_box_place_name==place_name)).first()

  @classmethod
  def get_unmatched_place_with_name_type(cls, place_name, type):
    return UnmatchedPlace.query.filter(and_(UnmatchedPlace.place_name==place_name, UnmatchedPlace.type==type)).first()

  @classmethod
  def add_unmatched_place(cls, place_name, type):
    place = cls.get_unmatched_place_with_name_type(place_name, type)
    if place:
      return True
    try:
      place = UnmatchedPlace(place_name=place_name, type=type)
      db.session.add(place)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def parse_address_by_map_box(cls, place_name):
    try:
      releveance = 0.7
      url = "https://api.tiles.mapbox.com/geocoding/v5/mapbox.places/{address}.json".format(address=quote_plus(place_name))
      querystring = {"country":"us","limit":"1","access_token": app.config['MAP_BOX_ACCESSTOKEN']}
      headers = {
          'cache-control': "no-cache",
          }
      response = requests.request("GET", url, headers=headers, params=querystring, proxies=None)
      result = json.loads(response.text)
      if len(result['features'])>0 and result['features'][0]['relevance']>= releveance:
        return result['features'][0]['place_name']
    except Exception as e:
      return place_name
    return place_name

  @classmethod
  def add_feed_back(cls, content):
    try:
      fb = FeedBack(content=content)
      db.session.add(fb)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def get_wechat_sessionkey_and_openid(cls, code):
    querystring = {
      'appid': app.config['WECHAT_APP_ID'],
      'secret': app.config['WECHAT_APP_SECRET'],
      'js_code': code,
      'grant_type': app.config['WECHAT_APP_GRANT_TYPE']
      }
    response = requests.request("GET", app.config['WECHAT_APP_CODE_URL'], params=querystring)
    return json.loads(response.text)

  @classmethod
  def get_user_with_openid(cls, openid):
    return User.query.filter_by(openid=openid).first()

  @classmethod
  def add_user(cls, openid, nick_name, gender, language, city, province, country, avatar_url, phone=None):
    user = cls.get_user_with_openid(openid=openid)
    if user:
      return user
    try:
      user = User(openid=openid, nick_name=nick_name, gender=gender,
        language=language, city=city, province=province, country=country, 
        avatar_url=avatar_url, phone=phone)
      db.session.add(user)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return None
    return user

  @classmethod
  def get_phone_with_phone_and_country(cls, phone, country):
    return Phone.query.filter_by(phone=phone, country=country).first()

  @classmethod
  def add_or_set_phone(cls, phone_nu, country, verification_code, verification_code_created_at, is_verified=False):
    phone = cls.get_phone_with_phone_and_country(phone=phone_nu, country=country)
    try:
      if not phone:
        phone = Phone(phone_nu, country, verification_code,
          verification_code_created_at, is_verified)
      else:
        phone.phone, phone.country = phone_nu, country
        phone.verification_code, is_verified = is_verified
        phone.verification_code_created_at = verification_code_created_at
      db.session.merge(phone)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return None
    return phone
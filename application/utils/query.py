from ..models import City, IndexPage, CityPage, HomePage, UnmatchedPlace, FeedBack, User, Phone, Collection, CityCount, CityRankingList, TotalRankingList
from ..models import SuperRankingList, CarouselFigure
from index import app, db
from flask import jsonify
from sqlalchemy import and_
import hashlib
from urllib import quote_plus
import requests
import json
from sqlalchemy.exc import DataError, IntegrityError
import datetime
import sys
from qiniu import Auth

FIVE_MINUTES = 60*5

class QueryHelper(object):
  'You can use this class query the complex query via the SqlAlchemy query'
  @classmethod
  def to_json_with_filter(cls, rows_dict, columns):
    d = {'success':True}
    for k, v in rows_dict.items():
      # handle the dict and integer and float
      if type(v) == type({}) or type(v) == type(1) or type(v) == type(1.0) or type(v) == type('') or type(v) == type(u'') or type(v) == type(True):
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
  def add_feed_back(cls, content, user_id):
    try:
      fb = FeedBack(content=content, user_id=user_id)
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
  def add_or_set_user(cls, openid, nick_name, gender, language, city, province, country, avatar_url, phone=None):
    user = cls.get_user_with_openid(openid=openid)
    if user:
      user.nick_name, user.gender = nick_name, gender
      user.language, user.city = language, city
      user.province, user.country = province, country
      user.avatar_url = avatar_url
    else:
      user = User(openid=openid, nick_name=nick_name, gender=gender,
        language=language, city=city, province=province, country=country, 
        avatar_url=avatar_url, phone=phone)
    try:
      db.session.merge(user)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return None
    return cls.get_user_with_openid(openid=openid)

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
        phone.verification_code, phone.is_verified = verification_code, is_verified
        phone.verification_code_created_at = verification_code_created_at
      db.session.merge(phone)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return None
    return phone

  @classmethod
  def get_phone_with_phone_and_country(cls, phone, country):
    return Phone.query.filter(and_(Phone.phone==phone, Phone.country==country)).first()

  @classmethod
  def verify_sms_code(cls, phone, country, code, expiration=FIVE_MINUTES):
    phone = cls.get_phone_with_phone_and_country(phone, country)
    if phone and phone.verification_code == code \
        and phone.verification_code_created_at + datetime.timedelta(seconds=expiration) > datetime.datetime.utcnow():
      return True 
    return False

  @classmethod
  def get_user_with_id(cls, user_id):
    return User.query.filter_by(id=user_id).first()

  @classmethod
  def set_user_phone_with_id(cls, user_id, phone, country_code, is_verified=True):
    user = cls.get_user_with_id(user_id=user_id)
    try:
      user.phone = phone
      user.country_code = country_code
      db.session.merge(user)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def set_phone_is_verified(cls, phone, country):
    phone = cls.get_phone_with_phone_and_country(phone=phone, country=country)
    try:
      phone.is_verified = True
      db.session.merge(phone)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def get_collection_with_user_home(cls, user_id, home_id):
    return Collection.query.filter(and_(Collection.user_id==user_id, Collection.home_id==home_id)).first()

  @classmethod
  def set_collection(cls, user_id, home_id):
    collection = cls.get_collection_with_user_home(user_id=user_id, home_id=home_id)
    if not collection:
      collection = Collection(user_id=user_id, home_id=home_id)
    else:
      collection.is_active = True

    try:
      db.session.merge(collection)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return None
    return cls.get_collection_with_user_home(user_id=user_id, home_id=home_id)

  @classmethod
  def del_collection(cls, user_id, home_id):
    collection = cls.get_collection_with_user_home(user_id=user_id, home_id=home_id)
    if not collection:
      return False
    collection.is_active = False
    try:
      db.session.merge(collection)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def get_collections_with_user(cls, user_id):
    return Collection.query.filter(and_(Collection.user_id==user_id, Collection.is_active==True)).all()

  @classmethod
  def get_city_count_with_date_and_city(cls, city_id, date):
    return CityCount.query.filter(and_(CityCount.city_id==city_id, CityCount.date==date)).first()

  @classmethod
  def get_city_ranking_list_with_city(cls, city_id, date):
    return CityRankingList.query.filter(and_(CityRankingList.city_id==city_id, CityRankingList.date==date)).order_by(
        CityRankingList.score.desc()).limit(10).all()

  @classmethod
  def get_total_ranking_list_with_city(cls, date):
    return TotalRankingList.query.filter_by(date=date).order_by(
        TotalRankingList.score.desc()).limit(10).all()

  @classmethod
  def get_super_ranking_list_with_city(cls):
    return SuperRankingList.query.filter_by(is_active=True).limit(10).all()

  @classmethod
  def get_carouse_figure(cls):
    return CarouselFigure.query.filter_by(is_active=True).all()

  @classmethod
  def pares_qiniu_pic(cls, key):
    q = Auth(app.config['QINIU_AK'], app.config['QINIU_SK'])
    return q.private_download_url(app.config['QINIU_DOMAIN']+key, app.config['QINIU_EXPIRES'])
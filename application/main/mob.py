from flask import request, jsonify, g
from flask import Blueprint
from index import app, db
from ..models import User
from index import session
from sqlalchemy.exc import IntegrityError
from ..utils.query import QueryHelper
from ..utils.helper import uuid_gen, json_validate, requires_token, generate_token, verify_token, id_generator

mob = Blueprint('mob', __name__)
logger = app.logger

@mob.route('/register', methods=['POST'])
@json_validate(filter=['token', 'userName', 'gender', 'country', 'phone', 'password', 'code'])
@requires_token
def register():
  incoming = request.get_json()
  user = User(openid=None, nick_name=incoming["userName"], gender=incoming['gender'], language=None, city=None, country=incoming["country"],
    province=None, avatar_url=None, phone=incoming["phone"], type=1, password=incoming["password"]
  )

  # Verify phone number
  if not QueryHelper.verify_sms_code(phone=incoming['phone'], country=incoming['country'], code=incoming['code']):
    logger.warning("Failed SMS Verification: {} entered a invalid code {}".format(incoming["phone"], incoming["country"], incoming["code"]))
    return jsonify(message="Phone has not been verified", success=False), 409

  db.session.add(user)

  try:
    db.session.commit()
  except IntegrityError as e:
    logger.warning("Failed User Creation: phone {}, {}".format(incoming["phone"], e))
    return jsonify(message="User with that phone already exists"), 409

  return jsonify(
    third_session=generate_token(user=user, session_key=None),
    success=True
  )

@mob.route('/login', methods=['POST'])
@json_validate(filter=['token', 'phone', 'code', 'country'])
@requires_token
def login():
  incoming = request.get_json()

  # Verify phone number
  if not QueryHelper.verify_sms_code(phone=incoming['phone'], country=incoming['country'], code=incoming['code']):
    logger.warning("Failed SMS Verification: {} entered a invalid code {}".format(incoming["phone"], incoming["country"], incoming["code"]))
    return jsonify(message="Phone has not been verified", success=False), 409  

  user = QueryHelper.get_user_with_phone_and_country(phone=incoming['phone'],
    country=incoming['country'])
  if not user:
    user = User(openid=None, nick_name=incoming["phone"][0:3]+'*'*4+incoming['phone'][7:], gender=None, language=None, city=None, country=incoming["country"],
    province=None, avatar_url=None, phone=incoming["phone"], type=1, password=None)
    try:
      db.session.add(user)
      db.session.commit()
    except IntegrityError as e:
      logger.warning("Failed User Creation: phone {}, {}".format(incoming["phone"], e))
      return jsonify(success=False, message='login failed'), 403
    user = QueryHelper.get_user_with_phone_and_country(phone=incoming['phone'],
      country=incoming['country'])
  
  third_session = generate_token(user=user, session_key=None)
  session[str(user.id)] = third_session
  return jsonify(
    third_session=third_session, success=True)

@mob.route('/get_hot_cities', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_hot_cities():
  columns = ['city_id', 'city_name', 'pic_url', 'increase_radio', 'rental_income_radio', 'button_pic_url',
    'button_dark_pic_url']
  d = {}
  l = []
  try:
    cities = QueryHelper.get_cities_filter_id(min_id=1, max_id=10)
    for city in cities:
      l.append({
        'city_id': city.id,
        'city_name': city.city_name,
        'pic_url': QueryHelper.pares_qiniu_pic(city.citypage.app_pic_url) if city.citypage else None,
        'increase_radio': city.citypage.increase_radio  if city.citypage else None,
        'rental_income_radio': city.citypage.rental_income_radio if city.citypage else None,
        'button_pic_url': QueryHelper.pares_qiniu_pic(city.citypage.button_pic_url) if city.citypage else None,
        'button_dark_pic_url': QueryHelper.pares_qiniu_pic(city.citypage.button_dark_pic_url) if city.citypage else None,
        })
      d['hot_cities'] = l
  except Exception as e:
    logger.error("Failed to get hot city list {}".format(e))
    return jsonify(success=False,
      message='Failed to get hot city list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@mob.route('/get_total_super_rank', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_total_super_rank():
  columns = ['index', 'address', 'score', 'ratio', 'total_pic', 'super_pic']
  d = {}
  try:
    l = []
    totals = QueryHelper.get_total_ranking_list_with_city()
    for idx, rank in enumerate(totals[0:3]):
      l.append({
        'index': idx,
        'address': rank.home.map_box_place_name,
        'score': rank.home.score,
        })
    d['total_pic'] = QueryHelper.pares_qiniu_pic(QueryHelper.get_app_rank_pic_with_type(type=1).pic_url)
    supers = QueryHelper.get_super_ranking_list_with_city()
    d['total_top_three'] = l
    l = []
    for idx, rank in enumerate(supers[0:3]):
      l.append({
        'index': idx,
        'address': rank.home.map_box_place_name,
        'ratio': (rank.rencent_price-rank.history_price)/rank.history_price,
        })
    d['super_pic'] = QueryHelper.pares_qiniu_pic(QueryHelper.get_app_rank_pic_with_type(type=2).pic_url)
    d['super_top_three'] = l
  except Exception as e:
    logger.error("Failed to get total super list {}".format(e))
    return jsonify(success=False,
      message='Failed to get total super list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@mob.route('/wechat/login', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'code'])
@requires_token
def wechat_login():
  incoming = request.get_json()
  # get access token
  access_token = QueryHelper.get_wechat_access_token_for_app(code=incoming['code'])
  if not access_token.get('access_token', None):
    logger.warning("Get wechat access_token failed {}".format(incoming["code"]))
    return jsonify(success=False, message='Get wechat access_token failed'), 403
  # get user info
  user_info = QueryHelper.get_wechat_user_info_for_app(access_token=access_token['access_token'],
    openid=access_token['openid'])
  user = QueryHelper.get_user_with_openid(openid=user_info['openid'])
  try:
    if not user:
      user = User(openid=user_info['openid'], nick_name=user_info['nickname'].encode('iso8859-1'), gender=user_info['sex'], language=None, city=None, country=user_info["country"],
      province=user_info['province'], avatar_url=user_info['headimgurl'], phone=None, type=1, password=None)
      db.session.add(user)
      db.session.commit()
      user = QueryHelper.get_user_with_openid(openid=user_info['openid'])
    else:
      user.nick_name = user_info['nickname'].encode('iso8859-1')
      user.avatar_url = user_info['headimgurl']
      db.session.merge(user)
      db.session.commit()
  except IntegrityError as e:
    logger.warning("Failed User Creation: phone openid {}, {}".format(user_info["openid"], e))
    return jsonify(success=False, message='login failed'), 403
  
  third_session = generate_token(user=user, session_key=None)
  session[str(user.id)] = third_session
  return jsonify(nick_name=user.nick_name, avatar_url=user.avatar_url, user_id=user.id,
    phone=user.phone, third_session=third_session, success=True)
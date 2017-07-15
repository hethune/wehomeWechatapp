# -*- coding: utf-8 -*-
from .models import City
from index import app, db
from .utils.helper import uuid_gen, json_validate, requires_token, generate_token, verify_token, requires_auth, id_generator
from .utils.query import QueryHelper
from .utils.cache import RedisCache
from flask import request, jsonify, g
import json
from tasks import send_sms_mobilecode
import datetime
from index import session

logger = app.logger
HALF_MINUTE = 30
TODAY_DATE = datetime.date.today().strftime('%Y-%m-%d')


@app.route('/api/index_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def index_page():
  columns = ['rental_radio', 'house_price_trend', 'increase_radio', 'rental_income_radio']
  d = {}
  try:
    index_page = QueryHelper.get_index_page()
    index_page.rental_radio = json.loads(index_page.rental_radio) if index_page.rental_radio else None
    index_page.house_price_trend = json.loads(index_page.house_price_trend) if index_page.house_price_trend else None
    index_page.increase_radio = json.loads(index_page.increase_radio) if index_page.increase_radio else None
    index_page.rental_income_radio = json.loads(index_page.rental_income_radio) if index_page.rental_income_radio else None
    d['index_page'] = index_page
  except Exception as e:
    logger.error("Failed to get index page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get index page list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_cities', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_cities():
  columns = ['id', 'city_name']
  d = {}
  try:
    index_page = QueryHelper.get_cities()
    d['city'] = index_page
  except Exception as e:
    logger.error("Failed to get city list {}".format(e))
    return jsonify(success=False,
      message='Failed to get city list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/city_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['city_id', 'token'])
@requires_token
def city_page():
  columns = ['sale_online_offline', 'rent_online_offline', 'house_sale_number', 'house_rent_number',
    'block_villa_max', 'block_villa_min', 'block_apartment_max', 'block_apartment_min', 'one_room_one_toilet',
    'two_room_two_toilet', 'three_room_two_toilet', 'rental_radio', 'house_price_trend', 'increase_radio',
    'rental_income_radio', 'list_average_price', 'deal_average_price', 'city_name', 'one_bed_one_bath_lower_bound',
    'one_bed_one_bath_upper_bound', 'two_bed_two_bath_lower_bound', 'two_bed_two_bath_upper_bound', 'three_bed_two_bath_lower_bound',
    'three_bed_two_bath_upper_bound', 'block_villa_median', 'block_apartment_median', 'today_sale_online', 'today_sale_offline',
    'today_rent_online', 'today_rent_offline', 'city_count', 'today_sale_online', 'today_sale_offline', 'today_rent_online', 'today_rent_offline',
    'diamond_room_num', 'gold_room_num', 'sliver_room_num', 'bronze_room_num']
  d = {}
  try:
    incoming = request.get_json()
    city_page = QueryHelper.get_city_page_with_city_id(city_id=incoming['city_id'])
    d['city_name'] = city_page.city.city_name
    city_page.rent_online_offline = json.loads(city_page.rent_online_offline) if city_page.rent_online_offline else None
    city_page.sale_online_offline = json.loads(city_page.sale_online_offline) if city_page.sale_online_offline else None
    city_page.house_price_trend = json.loads(city_page.house_price_trend) if city_page.house_price_trend else None
    city_page.one_room_one_toilet = json.loads(city_page.one_room_one_toilet) if city_page.one_room_one_toilet else None
    city_page.two_room_two_toilet = json.loads(city_page.two_room_two_toilet) if city_page.two_room_two_toilet else None
    city_page.three_room_two_toilet = json.loads(city_page.three_room_two_toilet) if city_page.three_room_two_toilet else None
    d['city_page'] = city_page
    # get the city count data
    with db.session.no_autoflush:
      d['city_count'] =  QueryHelper.get_city_count_with_date_and_city(city_id=incoming['city_id'],
        date=TODAY_DATE)
  except Exception as e:
    logger.error("Failed to get city page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get city page list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/home_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['place_name', 'token'])
@requires_token
def home_page():
  incoming = request.get_json()
  columns = ['map_box_place_name', 'score', 'house_price_dollar', 'exchange_rate',
    'rent', 'rental_radio', 'increase_radio', 'rental_income_radio',
    'neighborhood_rent_radio', 'city_name', 'city_trend', 'neighborhood_trend']
  d = {}
  place_name = incoming['place_name']
  try:
    if app.config['IS_PARSE_ADDRESS']:
      place_name = QueryHelper.parse_address_by_map_box(place_name=place_name)

    
    home_page = QueryHelper.get_home_page_with_place_name(place_name=place_name)
    if not home_page:
      QueryHelper.add_unmatched_place(place_name=incoming['place_name'], type='map_box_place_name')
      logger.error("Failed to get home page list we cant't find the given place")
      return jsonify(success=False,
        message="Failed to get home page list we cant't find the given place"), 409

    d['neighborhood_trend'] = json.loads(home_page.neighborhood.house_price_trend) if home_page.neighborhood.house_price_trend else None
    d['neighborhood_rent_radio']= home_page.neighborhood.neighbor_rental_radio
    d['city_trend'] = json.loads(home_page.city.citypage.house_price_trend) if home_page.city and home_page.city.citypage and home_page.city.citypage.house_price_trend else None
    d['city_name'] = home_page.city.city_name if home_page.city else None
    d['exchange_rate'] = QueryHelper.get_index_page().exchange_rate
    d['home_page'] = home_page

    # log the none value
    validate_d = {
      'score': home_page.score,
      'house_price_dollar': home_page.house_price_dollar,
      'rent': home_page.rent,
      'rental_radio': home_page.rental_radio,
      'increase_radio': home_page.increase_radio,
      'rental_income_radio': home_page.rental_income_radio,
      'neighborhood_rent_radio': home_page.neighborhood.neighbor_rental_radio,
      'city_trend': d['city_trend'],
      'neighborhood_trend': d['neighborhood_trend']
    }
    for k, v in validate_d.items():
      if not v:
        QueryHelper.add_unmatched_place(place_name=incoming['place_name'], type=k)

  except Exception as e:
    logger.error("Failed to get home page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get home page list'), 409
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/v2/home_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'third_session'])
@requires_token
@requires_auth
def v2_home_page():
  incoming = request.get_json()
  columns = ['map_box_place_name', 'score', 'house_price_dollar', 'exchange_rate',
    'rent', 'rental_radio', 'increase_radio', 'rental_income_radio',
    'neighborhood_rent_radio', 'city_name', 'city_trend', 'neighborhood_trend',
    'adjust_score', 'property_score', 'neighborhood_score']
  d = {}
  home_page = place_name = None
  try:
    if not incoming.get('home_id', None):
      place_name = incoming['place_name']
      if app.config['IS_PARSE_ADDRESS']:
        place_name = QueryHelper.parse_address_by_map_box(place_name=place_name)
      home_page = QueryHelper.get_home_page_with_place_name(place_name=place_name)
    else:
      home_page = QueryHelper.get_home_page_with_home_id(home_id=incoming['home_id'])

    if not home_page:
      QueryHelper.add_unmatched_place(
        place_name=incoming['place_name'] if incoming.get('place_name', None) else incoming.get('home_id'), type='map_box_place_name')
      logger.error("Failed to get home page list we cant't find the given place")
      return jsonify(success=False,
        message="Failed to get home page list we cant't find the given place"), 409

    d['id'] = home_page.id
    d['neighborhood_trend'] = json.loads(home_page.neighborhood.house_price_trend) if home_page.neighborhood.house_price_trend else None
    d['neighborhood_rent_radio']= home_page.neighborhood.neighbor_rental_radio if home_page.neighborhood else None
    d['neighborhood_score'] = home_page.neighborhood_score if home_page.neighborhood_score else None
    d['city_trend'] = json.loads(home_page.city.citypage.house_price_trend) if home_page.city and home_page.city.citypage and home_page.city.citypage.house_price_trend else None
    d['city_name'] = home_page.city.city_name if home_page.city else None
    d['exchange_rate'] = QueryHelper.get_index_page().exchange_rate
    d['home_page'] = home_page
    d['favorite'] = True if QueryHelper.get_collection_with_user_home(user_id=g.current_user['id'], home_id=home_page.id) else False

    # log the none value
    validate_d = {
      'score': home_page.score,
      'house_price_dollar': home_page.house_price_dollar,
      'rent': home_page.rent,
      'rental_radio': home_page.rental_radio,
      'increase_radio': home_page.increase_radio,
      'rental_income_radio': home_page.rental_income_radio,
      'neighborhood_rent_radio': home_page.neighborhood.neighbor_rental_radio,
      'city_trend': d['city_trend'],
      'neighborhood_trend': d['neighborhood_trend']
    }
    for k, v in validate_d.items():
      if not v:
        QueryHelper.add_unmatched_place(place_name=incoming['place_name'], type=k)

  except Exception as e:
    logger.error("Failed to get home page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get home page list'), 409
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/set_feedback', methods=['POST'])
@uuid_gen
@json_validate(filter=['content', 'token', 'third_session'])
@requires_token
@requires_auth
def set_feedback():
  incoming = request.get_json()
  is_success = QueryHelper.add_feed_back(content=incoming['content'], user_id=g.current_user['id'])
  if not is_success:
    logger.error('Failed to set feed back')
    return jsonify(success=False,
      message='Failed to set feed back'), 409
  return jsonify(success=True,
      message='Success to set feed back')

@app.route('/api/login', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'code', 'rawdata'])
@requires_token
def login():
  incoming = request.get_json()
  # get wechat sssion key and openid
  result = QueryHelper.get_wechat_sessionkey_and_openid(incoming['code'])
  if not result.get('session_key', None):
    logger.error('Failed to login')
    return jsonify(success=False,
      message='Failed to login'), 409

  # if not register then regist and return 3rd_session
  user = QueryHelper.add_or_set_user(openid=result['openid'], nick_name=incoming['rawdata']['nickName'],
    gender=incoming['rawdata']['gender'], language=incoming['rawdata']['language'], city=incoming['rawdata']['city'],
    province=incoming['rawdata']['province'], country=incoming['rawdata']['country'], avatar_url=incoming['rawdata']['avatarUrl'])
  if not user:
    logger.error('Failed to login')
    return jsonify(success=False,
      message='Failed to login'), 409
  # if not fill the phone number then send sms message and validate

  third_session = generate_token(user, result['session_key'])
  session[str(user.id)] = third_session

  if not user.phone:
    return jsonify(success=False, status=0, user_id=user.id,
      message='Phone not verifed', third_session=session[str(user.id)])
  return jsonify(success=True, user_id=user.id, third_session=session[str(user.id)])

@app.route("/api/send_mobile_code", methods=["POST"])
@uuid_gen
@json_validate(filter=['token', 'phone', 'country'])
@requires_token
def send_mobile_code():
  incoming = request.get_json()
  verification_code = id_generator()
  phone = QueryHelper.get_phone_with_phone_and_country(phone=incoming["phone"], country=incoming["country"])
  if phone:
    if phone.verification_code_created_at \
      and phone.verification_code_created_at + datetime.timedelta(seconds=HALF_MINUTE) > datetime.datetime.utcnow():
      logger.warning("{} is sending sms code too frequently".format(incoming["phone"]))
      return jsonify(message="Trying too frequent"), 409

  QueryHelper.add_or_set_phone(phone_nu=incoming['phone'], country=incoming['country'],
    verification_code=verification_code, verification_code_created_at=datetime.datetime.utcnow())

  # send_sms async
  send_sms_mobilecode.apply_async((incoming["phone"], incoming["country"], verification_code))
  return jsonify(success=True)

@app.route("/api/verify_mobile_code", methods=["POST"])
@uuid_gen
@json_validate(filter=['token', 'phone', 'country', 'code', 'user_id'])
@requires_token
def verify_mobile_code():
  incoming = request.get_json()
  if not QueryHelper.verify_sms_code(phone=incoming['phone'], country=incoming['country'], code=incoming['code']):
    logger.error('Verify the sms code failed')
    return jsonify(success=False, message='Verify the sms code failed')

  user = QueryHelper.get_user_with_id(user_id=incoming['user_id'])
  is_phone_success = QueryHelper.set_user_phone_with_id(user_id=incoming['user_id'], phone=incoming['phone'], country_code=incoming['country'])
  is_code_success = QueryHelper.set_phone_is_verified(phone=incoming['phone'], country=incoming['country'])
  if not is_phone_success or not is_code_success:
    logger.error('Verify the sms code failed')
    return jsonify(success=False, message='Verify the sms code failed')

  return jsonify(success=True, message='Verify the sms code successfully')

@app.route('/ping', methods=['GET'])
def ping():
  return 'pong'

@app.route('/api/set_collection', methods=['POST'])
@uuid_gen
@json_validate(filter=['home_id', 'token', 'third_session'])
@requires_token
@requires_auth
def set_collection():
  incoming = request.get_json()
  is_success = QueryHelper.set_collection(user_id=g.current_user['id'], home_id=incoming['home_id'])
  if not is_success:
    logger.error('Failed to set collection user: {user_id} home: {home_id}'.format(
      user_id=g.current_user['id'], home_id=incoming['home_id']))
    return jsonify(success=False,
      message='Failed to set collection'), 409
  return jsonify(success=True,
      message='Success to set cllection')

@app.route('/api/get_collections', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'third_session'])
@requires_token
@requires_auth
def get_collections():
  incoming = request.get_json()
  columns = ['map_box_place_name', 'score']
  d = {}
  l = []
  try:
    collections = QueryHelper.get_collections_with_user(user_id=g.current_user['id'])
    for item in collections:
      l.append({
        'map_box_place_name': item.homepage.map_box_place_name,
        'score': item.homepage.score
        })
    d['collections'] = l
  except Exception as e:
    logger.error("Failed to get collecions list {}".format(e))
    return jsonify(success=False,
      message='Failed to get collecions list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)


@app.route('/api/del_collection', methods=['POST'])
@uuid_gen
@json_validate(filter=['home_id', 'token', 'third_session'])
@requires_token
@requires_auth
def del_collection():
  incoming = request.get_json()
  is_success = QueryHelper.del_collection(user_id=g.current_user['id'], home_id=incoming['home_id'])
  if not is_success:
    logger.error('Failed to del collection user: {user_id} home: {home_id}'.format(
      user_id=g.current_user['id'], home_id=incoming['home_id']))
    return jsonify(success=False,
      message='Failed to del collection'), 409
  return jsonify(success=True,
      message='Success to del cllection')

@app.route('/api/get_city_ranking_list', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'city_id'])
@requires_token
def get_city_ranking_list():
  incoming = request.get_json()
  columns = ['score', 'rental_radio', 'increase_radio', 'map_box_place_name', 'house_price_dollar',
    'pic_url', 'city_name', 'home_id']
  d = {}
  l = []
  try:
    ranks = QueryHelper.get_city_ranking_list_with_city(city_id=incoming['city_id'], date=TODAY_DATE)
    for item in ranks:
      l.append({
        'home_id': item.home.id,
        'score': item.score,
        'rental_radio': item.home.rental_radio,
        'increase_radio': item.home.increase_radio,
        'map_box_place_name': item.home.map_box_place_name,
        'house_price_dollar': item.home.house_price_dollar,
        'pic_url': QueryHelper.pares_qiniu_pic(item.pic_url),
        'city_name': item.city.city_name
        })
    d['city_ranking_list'] = l
  except Exception as e:
    logger.error("Failed to get city ranking list {}".format(e))
    return jsonify(success=False,
      message='Failed to get city ranking list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_total_ranking_list', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_total_ranking_list():
  incoming = request.get_json()
  columns = ['score', 'rental_radio', 'increase_radio', 'map_box_place_name', 'house_price_dollar', 'pic_url',
    'home_id']
  d = {}
  l = []
  try:
    ranks = QueryHelper.get_total_ranking_list_with_city(date=TODAY_DATE)
    for item in ranks:
      l.append({
        'home_id': item.home.id,
        'score': item.score,
        'rental_radio': item.home.rental_radio,
        'increase_radio': item.home.increase_radio,
        'map_box_place_name': item.home.map_box_place_name,
        'house_price_dollar': item.home.house_price_dollar,
        'pic_url': QueryHelper.pares_qiniu_pic(item.pic_url)
        })
    d['total_ranking_list'] = l
  except Exception as e:
    logger.error("Failed to get total ranking list {}".format(e))
    return jsonify(success=False,
      message='Failed to get total ranking list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_super_ranking_list', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_super_ranking_list():
  incoming = request.get_json()
  columns = ['history_date', 'recent_date', 'history_price', 'rencent_price', 'pic_url',
    'home_id', 'map_box_place_name']
  d = {}
  l = []
  try:
    ranks = QueryHelper.get_super_ranking_list_with_city()
    for item in ranks:
      l.append({
        'map_box_place_name': item.home.map_box_place_name,
        'home_id': item.home.id,
        'history_date': item.history_date,
        'recent_date': item.recent_date,
        'history_price': item.history_price,
        'rencent_price': item.rencent_price,
        'pic_url': QueryHelper.pares_qiniu_pic(item.pic_url),
        })
    d['super_ranking_list'] = l
  except Exception as e:
    logger.error("Failed to get super ranking list {}".format(e))
    return jsonify(success=False,
      message='Failed to get super ranking list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_carouse_figure', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_carouse_figure():
  incoming = request.get_json()
  columns = ['index', 'pic_url']
  d = {}
  l = []
  try:
    ranks = QueryHelper.get_carouse_figure()
    for item in ranks:
      l.append({
        'index': item.index,
        'pic_url': QueryHelper.pares_qiniu_pic(item.pic_url)
        })
    d['carouse_figure'] = l
  except Exception as e:
    logger.error("Failed to get carouse figure list {}".format(e))
    return jsonify(success=False,
      message='Failed to get carouse figure list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)
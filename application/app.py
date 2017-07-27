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
import time

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
    'diamond_room_num', 'gold_room_num', 'sliver_room_num', 'bronze_room_num', 'pic_url', 'is_collectd']
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
    city_page.pic_url = QueryHelper.pares_qiniu_pic(city_page.pic_url) if city_page.pic_url else None
    d['city_page'] = city_page
    # get the city count data
    with db.session.no_autoflush:
      # d['is_collectd'] = True if QueryHelper.get_collection_with_user_and_city(user_id=g.current_user['id'], city_id=incoming['city_id']) else False
      d['city_count'] =  QueryHelper.get_city_count_with_date_and_city(city_id=incoming['city_id'],
        date=TODAY_DATE)
  except Exception as e:
    logger.error("Failed to get city page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get city page list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/v2/city_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['city_id', 'token', 'third_session'])
@requires_token
@requires_auth
def v2_city_page():
  columns = ['sale_online_offline', 'rent_online_offline', 'house_sale_number', 'house_rent_number',
    'block_villa_max', 'block_villa_min', 'block_apartment_max', 'block_apartment_min', 'one_room_one_toilet',
    'two_room_two_toilet', 'three_room_two_toilet', 'rental_radio', 'house_price_trend', 'increase_radio',
    'rental_income_radio', 'list_average_price', 'deal_average_price', 'city_name', 'one_bed_one_bath_lower_bound',
    'one_bed_one_bath_upper_bound', 'two_bed_two_bath_lower_bound', 'two_bed_two_bath_upper_bound', 'three_bed_two_bath_lower_bound',
    'three_bed_two_bath_upper_bound', 'block_villa_median', 'block_apartment_median', 'today_sale_online', 'today_sale_offline',
    'today_rent_online', 'today_rent_offline', 'city_count', 'today_sale_online', 'today_sale_offline', 'today_rent_online', 'today_rent_offline',
    'diamond_room_num', 'gold_room_num', 'sliver_room_num', 'bronze_room_num', 'pic_url', 'is_collectd']
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
    city_page.pic_url = QueryHelper.pares_qiniu_pic(city_page.pic_url) if city_page.pic_url else None
    d['city_page'] = city_page
    # get the city count data
    with db.session.no_autoflush:
      d['is_collectd'] = True if QueryHelper.get_collection_with_user_and_city(user_id=g.current_user['id'], city_id=incoming['city_id']) else False
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
  logger.info('v2_home_page start {}'.format(time.time()))
  incoming = request.get_json()
  if not QueryHelper.validate_query_frequency_grant(user_id=g.current_user['id'], date=TODAY_DATE):
    logger.error("The user's query frequency is out of limit")
    return jsonify(success=False,
      message="The user's query frequency is out of limit"), 409
  logger.info('v2_home_page validate_query_frequency_grant {}'.format(time.time()))
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
        logger.info('v2_home_page parse_address_by_map_box {}'.format(time.time()))
      home_page = QueryHelper.get_home_page_with_place_name(place_name=place_name)
      logger.info('v2_home_page get_home_page_with_place_name {}'.format(time.time()))
    else:
      home_page = QueryHelper.get_home_page_with_home_id(home_id=incoming['home_id'])
      logger.info('v2_home_page get_home_page_with_home_id {}'.format(time.time()))
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
    logger.info('v2_home_page validate data {}'.format(time.time()))

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
        QueryHelper.add_unmatched_place(place_name=incoming.get('place_name', None), type=k)
    logger.info('v2_home_page log data {}'.format(time.time()))

  except Exception as e:
    logger.error("Failed to get home page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get home page list'), 409
  logger.info('v2_home_page finish {}'.format(time.time()))
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/v3/home_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'third_session'])
@requires_token
@requires_auth
def v3_home_page():
  logger.info('v3_home_page start {}'.format(time.time()))
  incoming = request.get_json()
  if not QueryHelper.validate_query_frequency_grant(user_id=g.current_user['id'], date=TODAY_DATE):
    logger.error("The user's query frequency is out of limit v3")
    return jsonify(success=False,
      message="The user's query frequency is out of limit"), 409
  logger.info('v3_home_page validate_query_frequency_grant {}'.format(time.time()))
  columns = ['map_box_place_name', 'score', 'house_price_dollar', 'exchange_rate',
    'rent', 'rental_radio', 'increase_radio', 'rental_income_radio',
    'neighborhood_rent_radio', 'city_name', 'city_trend', 'neighborhood_trend',
    'adjust_score', 'property_score', 'neighborhood_score', 'apartment', 'home_id', 'apt_no']
  d = {}
  l = []
  home_page = place_name = None
  try:
    if not incoming.get('home_id', None):
      # home_id is None
      place_name = incoming['place_name']
      if app.config['IS_PARSE_ADDRESS']:
        place_name = QueryHelper.parse_address_by_map_box(place_name=place_name)
        logger.info('v3_home_page parse_address_by_map_box {}'.format(time.time()))
      home_page = QueryHelper.get_home_page_with_place_name(place_name=place_name)
      logger.info('v3_home_page get_home_page_with_place_name {}'.format(time.time()))
    else:
      # home_id is not None
      home_page = QueryHelper.get_home_page_with_home_id(home_id=incoming['home_id'])
      logger.info('v3_home_page get_home_page_with_home_id {}'.format(time.time()))

    if not home_page:
      QueryHelper.add_unmatched_place(
        place_name=incoming['place_name'] if incoming.get('place_name', None) else incoming.get('home_id'), type='map_box_place_name')
      logger.error("Failed to get home page list we cant't find the given place v3")
      return jsonify(success=False,
        message="Failed to get home page list we cant't find the given place v3"), 409
    elif home_page.apt_no and not incoming.get('home_id', None):
      homes = QueryHelper.get_apartment_no_with_place_name(place_name)
      print homes
      for home in homes:
        l.append({
          'home_id': home.id,
          'apt_no': home.apt_no,
          'map_box_place_name': home.map_box_place_name
          })
      d['apartment'] = l
      return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

    d['id'] = home_page.id
    d['neighborhood_trend'] = json.loads(home_page.neighborhood.house_price_trend) if home_page.neighborhood.house_price_trend else None
    d['neighborhood_rent_radio']= home_page.neighborhood.neighbor_rental_radio if home_page.neighborhood else None
    d['neighborhood_score'] = home_page.neighborhood_score if home_page.neighborhood_score else None
    d['city_trend'] = json.loads(home_page.city.citypage.house_price_trend) if home_page.city and home_page.city.citypage and home_page.city.citypage.house_price_trend else None
    d['city_name'] = home_page.city.city_name if home_page.city else None
    d['exchange_rate'] = QueryHelper.get_index_page().exchange_rate
    d['home_page'] = home_page
    d['favorite'] = True if QueryHelper.get_collection_with_user_home(user_id=g.current_user['id'], home_id=home_page.id) else False
    logger.info('v3_home_page validate data {}'.format(time.time()))

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
        QueryHelper.add_unmatched_place(place_name=incoming.get('place_name', None), type=k)
    logger.info('v3_home_page log data {}'.format(time.time()))

  except Exception as e:
    logger.error("v3 Failed to get home page list {}".format(e))
    return jsonify(success=False,
      message='v3 Failed to get home page list'), 409
  logger.info('v3_home_page finish {}'.format(time.time()))
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
    logger.error('Failed to get session key {code} {result}'.format(code=incoming['code'], result=result))
    return jsonify(success=False,
      message='Failed to get session key'), 409

  # if not register then regist and return 3rd_session
  user = QueryHelper.add_or_set_user(openid=result['openid'], nick_name=incoming['rawdata']['nickName'],
    gender=incoming['rawdata']['gender'], language=incoming['rawdata']['language'], city=incoming['rawdata']['city'],
    province=incoming['rawdata']['province'], country=incoming['rawdata']['country'], avatar_url=incoming['rawdata']['avatarUrl'])
  if not user:
    logger.error('Failed to get user')
    return jsonify(success=False,
      message='Failed to login'), 409
  # if not fill the phone number then send sms message and validate

  third_session = generate_token(user, result['session_key'])
  session[str(user.id)] = third_session

  if not user.phone:
    logger.error('Phone not verifed {third_session}'.format(third_session=session[str(user.id)]))
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
  columns = ['map_box_place_name', 'score', 'id']
  d = {}
  l = []
  try:
    collections = QueryHelper.get_collections_with_user(user_id=g.current_user['id'])
    for item in collections:
      l.append({
        'map_box_place_name': item.homepage.map_box_place_name,
        'score': item.homepage.score,
        'id': item.homepage.id
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
    'pic_url', 'city_name', 'home_id', 'rental_income_radio']
  d = {}
  l = []
  try:
    ranks = QueryHelper.get_city_ranking_list_with_city(city_id=incoming['city_id'], date=TODAY_DATE)
    for item in ranks:
      l.append({
        'home_id': item.home.id,
        'score': item.home.score,
        'rental_income_radio': item.home.rental_income_radio,
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
    'home_id', 'rental_income_radio']
  d = {}
  l = []
  try:
    ranks = QueryHelper.get_total_ranking_list_with_city(date=TODAY_DATE)
    for item in ranks:
      l.append({
        'home_id': item.home.id,
        'score': item.home.score,
        'rental_radio': item.home.rental_radio,
        'increase_radio': item.home.increase_radio,
        'map_box_place_name': item.home.map_box_place_name,
        'house_price_dollar': item.home.house_price_dollar,
        'rental_income_radio': item.home.rental_income_radio,
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

@app.route('/api/v2/get_carouse_figure', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def v2_get_carouse_figure():
  incoming = request.get_json()
  columns = ['index', 'pic_url']
  d = {}
  l = []
  try:
    ranks = QueryHelper.v2_get_carouse_figure()
    for item in ranks:
      l.append({
        'index': item.index,
        'pic_url': QueryHelper.pares_qiniu_pic(item.pic_url)
        })
    d['carouse_figure'] = l
  except Exception as e:
    logger.error("Failed to get v2 carouse figure list {}".format(e))
    return jsonify(success=False,
      message='Failed to get v2 carouse figure list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_answer', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_answer():
  return jsonify(success=True, answer_url=QueryHelper.pares_qiniu_pic(key=QueryHelper.get_answer_url().pic_url))

@app.route('/api/set_city_collections', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'city_ids', 'third_session'])
@requires_token
@requires_auth
def set_city_collections():
  incoming = request.get_json()
  is_success = QueryHelper.set_city_collections(user_id=g.current_user['id'], city_ids=incoming['city_ids'])
  if not is_success:
    logger.error('Failed to set city collections user: {user_id} city: {city_id}'.format(
      user_id=g.current_user['id'], city_id=incoming['city_id']))
    return jsonify(success=False,
      message='Failed to set city collections'), 409
  return jsonify(success=True,
      message='Success to set city cllections')

@app.route('/api/del_city_collection', methods=['POST'])
@uuid_gen
@json_validate(filter=['city_id', 'token', 'third_session'])
@requires_token
@requires_auth
def del_city_collection():
  incoming = request.get_json()
  is_success = QueryHelper.del_city_collection(user_id=g.current_user['id'], city_id=incoming['city_id'])
  if not is_success:
    logger.error('Failed to del city collection user: {user_id} city: {city_id}'.format(
      user_id=g.current_user['id'], city_id=incoming['city_id']))
    return jsonify(success=False,
      message='Failed to del city collection'), 409
  return jsonify(success=True,
      message='Success to del city cllection')

@app.route('/api/set_read_condition', methods=['POST'])
@uuid_gen
@json_validate(filter=['city_id', 'token', 'third_session'])
@requires_token
@requires_auth
def set_read_condition():
  incoming = request.get_json()
  ranks = QueryHelper.get_city_ranking_list_with_city(city_id=incoming['city_id'])
  is_success = QueryHelper.set_read_condition(user_id=g.current_user['id'],
    city_id=incoming['city_id'], rank_date=ranks[0].created_at.strftime('%Y-%m-%d'))
  if not is_success:
    logger.error('Failed to set read condition user: {user_id} city: {city_id}'.format(
      user_id=g.current_user['id'], city_id=incoming['city_id']))
    return jsonify(success=False,
      message='Failed to set read condition'), 409
  return jsonify(success=True,
      message='Success to set read condition')

@app.route('/api/get_city_collections', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'third_session'])
@requires_token
@requires_auth
def get_city_collections():
  incoming = request.get_json()
  columns = ['city_id', 'city_name', 'increase_radio', 'rental_income_radio']
  d = {}
  l = []
  try:
    collecions = QueryHelper.get_city_collections(user_id=g.current_user['id'])
    for collection in collecions:
      l.append({
        'city_id': collection.city.id,
        'city_name': collection.city.city_name,
        'increase_radio': collection.city.citypage.rental_income_radio,
        'rental_income_radio': collection.city.citypage.rental_income_radio,
        })
    d['city_collections'] = l
  except Exception as e:
    logger.error("Failed to get city collection list {}".format(e))
    return jsonify(success=False,
      message='Failed to get city collection list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_today_new_home', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_token
def get_today_new_home():
  incoming = request.get_json()
  columns = ['total', 'home', 'score','map_box_place_name',
    'rental_income_radio', 'increase_radio', 'pic_url', 'last_updated']
  d = {}
  l = []
  try:
    home_page, total, rank_id = QueryHelper.get_today_first_new_home()
    all_homes = QueryHelper.get_newest_all_city_ranking_list()
    d['total'] = len(all_homes)
    d['last_updated'] = all_homes[0].updated_at
    d['home'] = home_page
    d['pic_url'] = QueryHelper.pares_qiniu_pic(QueryHelper.get_index_page_card_pic_url().pic_url)
  except Exception as e:
    logger.error("Failed to get today new home {}".format(e))
    return jsonify(success=False,
      message='Failed to get today new home')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_all_or_follow_homes', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'third_session'])
@requires_token
@requires_auth
def get_all_or_follow_homes():
  incoming = request.get_json()
  ranks = None
  columns = ['house_price_dollar', 'rental_income_radio', 'increase_radio', 'score', 'pic_url', 'city_name', 'home_id']
  d = {}
  l = []
  try:
    rank_ids = QueryHelper.get_today_new_home_with_user(user_id=g.current_user['id'])
    if len(rank_ids) == 0:
      ranks = QueryHelper.get_newest_all_city_ranking_list()
    else:
      ranks = QueryHelper.get_newest_follow_city_ranking_list(ids=[item[0] for item in rank_ids])
    for rank in ranks:
      if d.get(rank.city.id, None) is None:
        d[rank.city.id] = []
      d[rank.city.id].append({
        'city_name': rank.city.city_name,
        'house_price_dollar': rank.home.house_price_dollar,
        'rental_income_radio': rank.home.rental_income_radio,
        'increase_radio': rank.home.increase_radio,
        'score': rank.score,
        'home_id': rank.home.id,
        'pic_url': QueryHelper.pares_qiniu_pic(rank.pic_url)
        })
  except Exception as e:
    logger.error("Failed to get all new homes list {}".format(e))
    return jsonify(success=False,
      message='Failed to get all new homes list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)
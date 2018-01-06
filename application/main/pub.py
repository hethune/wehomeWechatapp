from flask import request, jsonify, g
from flask import Blueprint
from index import app, db, home_cache
from ..models import User,HomePage
from index import session
from flask.json import dumps
from sqlalchemy.exc import IntegrityError
from ..utils.query import QueryHelper
from ..utils.helper import uuid_gen, json_validate, requires_token, generate_token, verify_token, id_generator,increment,require_app
from ..utils.count import Count
import time
import re
import json

ALLOW_CITY_ID = [1,2,4,10,3,8,9,5,6]
company = Blueprint('company', __name__)
logger = app.logger

@company.route('/api/autocomplete',methods=['POST'])
@json_validate(filter=['query'])
@require_app
@increment(count_type=Count.AUTOCOMPLETE_TYPE)
def autocomplete():
  incoming = request.get_json()
  data = []
  if 'query' in incoming:
    try:
      value = [r for r in re.split('[-,; ]',incoming['query'].strip()) if r]
      mores = ["UPPER(map_box_place_name) LIKE UPPER('%{}%')".format(v) for v in value]
      query_part = " AND ".join(mores)
      query =  """
        SELECT map_box_place_name,city_id
        FROM home_page
        WHERE
        """ + query_part
      homes = db.session.execute(query)
      for h in homes.fetchall():
        if h[0] not in data and h[1] in ALLOW_CITY_ID:
          data.append(h[0])
        if len(data)==5:
          break
    except Exception as e:
      logger.error("autocomplete failed:{}".format(e))
  return jsonify(success=True,data=data)

@company.route('/api/pub/home_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['place_name'])
@require_app
@increment(count_type=Count.PROPERTY_TYPE)
#requires_token
def company_home_page():
  logger.info('company query start {}'.format(time.time()))
  incoming = request.get_json()

  columns = ['map_box_place_name', 'bedroom', 'bathroom','size','latitude','longitude','house_price_dollar','score', 'exchange_rate',
    'rent','increase_radio', 'rental_income_radio', 'city_name', 'city_trend', 'neighborhood_trend','apartment', 'home_id','exchange_rate','description','nearby_school','price_history']

  d = {}
  l = []
  home_page = place_name = None
  try:
    if not incoming.get('home_id', None):
      # home_id is None
      place_name = incoming['place_name']
      if app.config['IS_PARSE_ADDRESS']:
        place_name = QueryHelper.parse_address_by_map_box(place_name=place_name)
        logger.info('company_home_page parse_address_by_map_box {}'.format(time.time()))

      if app.config['IS_HOME_CACHE'] and home_cache[place_name]:
        return QueryHelper.to_response(data=json.loads(home_cache[place_name]))

      home_page = QueryHelper.get_home_page_with_place_name(place_name=place_name)
      logger.info('company_home_page get_home_page_with_place_name {}'.format(time.time()))
    else:
      # home_id is not None get home cache by home_id
      if app.config['IS_HOME_CACHE'] and home_cache[str(incoming['home_id'])]:
        return QueryHelper.to_response(data=json.loads(home_cache[str(incoming['home_id'])]))

      home_page = QueryHelper.get_home_page_with_home_id(home_id=incoming['home_id'])
      logger.info('company_home_page get_home_page_with_home_id {}'.format(time.time()))

    if not home_page:
      logger.error("Failed to get home page list we cant't find the given place")
      if app.config['IS_SIMILAR']:
        result = QueryHelper.get_home_page_id_with_place_name(place_name=place_name)
        home_page = QueryHelper.get_home_page_with_home_id(home_id=result[0][0])

    #if home_page and home_page.apt_no and not incoming.get('home_id', None):
    #  homes = QueryHelper.get_apartment_no_with_place_name(place_name)
    #  for home in homes:
    #    l.append({
    #      'home_id': home.id,
    #      'apt_no': home.apt_no,
    #      'map_box_place_name': home.map_box_place_name
    #      })
    #  d['apartment'] = l
    #  result_dict = QueryHelper.to_dict_with_filter(rows_dict=d, columns=columns)
    #  result_json = dumps(result_dict)
    #if app.config['IS_HOME_CACHE']:
    #  home_cache.set_key_value(name=home.map_box_place_name, value=result_json, expiration=app.config['REDIS_HOME_CACHE_EXPIRE_TIME'])
    #  return jsonify(result_dict), 200

    if not home_page:
      QueryHelper.add_unmatched_place(
        place_name=incoming['place_name'] if incoming.get('place_name', None) else incoming.get('home_id'), type='map_box_place_name')
      logger.error("Failed to get home page list we cant't find the given place")
      return jsonify(success=False,
        message="Failed to get home page list we cant't find the given place"), 409

    d['id'] = home_page.id
    d['neighborhood_trend'] = json.loads(home_page.neighborhood.house_price_trend) if home_page.neighborhood.house_price_trend else None
    d['city_trend'] = json.loads(home_page.city.citypage.house_price_trend) if home_page.city and home_page.city.citypage and home_page.city.citypage.house_price_trend else None
    d['city'] = {}
    d['city']['name'] = home_page.city.city_name if home_page.city else None
    d['city']['deal_price'] = home_page.city.citypage.deal_average_price
    d['city']['list_price'] = home_page.city.citypage.list_average_price

    d['property'] = home_page
    d['exchange_rate'] = QueryHelper.get_index_page().exchange_rate
    logger.info('company_home_page validate data {}'.format(time.time()))

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
    logger.info('company_home_page log data {}'.format(time.time()))

  except Exception as e:
    logger.info('company query failed {},{}'.format(time.time(),e))
    return jsonify(success=False,
      message='Failed to get home page list'), 409

  logger.info('company_home_page finish {}'.format(time.time()))
  result_dict = QueryHelper.to_dict_with_filter(rows_dict=d, columns=columns)

  # further process result_dict
  result_dict['property']['house_price'] = result_dict['property'].pop('house_price_dollar')
  result_dict['property']['description'] = result_dict['property']['description'].strip('Note: This property is not currently for sale or for rent. The description below may be from a previous listing.') if result_dict['property']['description'] else None
  result_dict['property']['downpayment'] = 0.25
  if result_dict['property']['increase_radio'] and result_dict['property']['rental_income_radio']:
    result_dict['property']['return'] = result_dict['property'].pop('increase_radio')+result_dict['property'].pop('rental_income_radio')
  else:
    result_dict['property']['return'] = None
    result_dict['property'].pop('increase_radio')
    result_dict['property'].pop('rental_income_radio')
  trend = result_dict['city_trend'].values()
  result_dict['city']['city_trend'] = {'history':trend[0]}
  result_dict.pop('city_trend')

  result_json = dumps(result_dict)
  if app.config['IS_HOME_CACHE']:
    home_cache.set_key_value(name=home_page.id, value=result_json, expiration=app.config['REDIS_HOME_CACHE_EXPIRE_TIME'])
    home_cache.set_key_value(name=home_page.map_box_place_name, value=result_json, expiration=app.config['REDIS_HOME_CACHE_EXPIRE_TIME'])
  return jsonify(result_dict), 200

@company.route('/api/pub/city_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['city_id'])
@require_app
@increment(count_type=Count.CITY_TYPE)
def company_city_page():
  columns = ['house_price_trend', 'city_name','return','house_price','bedroom','bathroom','size','pic_url','type']
  d = {}
  try:
    incoming = request.get_json()
    city_page = QueryHelper.get_city_page_with_city_id(city_id=incoming['city_id'])
    d['city_name'] = city_page.city.city_name
    trend = json.loads(city_page.house_price_trend)
    d['list_price'] = city_page.list_average_price
    d['trend'] = {'history':trend.values()[0]}
    d['return'] = city_page.increase_radio+city_page.rental_income_radio
    rooms_=QueryHelper.get_home_pages_with_query(incoming['city_id'],offset=1,limit=10,**{'hq':1})
    d['rooms'] = rooms_[0]
    for r in rooms_[0]:
      r.type = 'Apartment' if r.apt_no else 'Single Family House'
      r.house_price = r.house_price_dollar
    result_dict = QueryHelper.to_dict_with_filter(rows_dict=d, columns=columns)
    d['hq_length'] = rooms_[1]
  except Exception as e:
    logger.error("Failed to get city page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get city page list')
  result = QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)
  return result


@company.route('/api/pub/listing', methods=['POST'])
@uuid_gen
@json_validate(filter=['city_id','offset','limit'])
@require_app
@increment(count_type=Count.LISTING_TYPE)
def listing_page():
  d = {}
  columns = ['id','room_type','map_box_place_name','house_price','size','city_id','bedroom','pic_url','length','type']
  try:
    incoming = request.get_json()
    shorter_incoming = {k:incoming[k] for k in incoming.keys() if k not in ['city_id','offset','limit']}
    city_id = incoming['city_id']

    rooms_ = QueryHelper.get_home_pages_with_query(city_id=city_id,offset=int(incoming['offset']),limit=int(incoming['limit']),**shorter_incoming)
    d['rooms'] = rooms_[0]

    # pre-process
    for r in rooms_[0]:
      r.type = 'Apartment' if r.apt_no else 'Single Family House'
      r.house_price = r.house_price_dollar
    result_dict = QueryHelper.to_dict_with_filter(rows_dict=d, columns=columns)
    result_dict['length']=rooms_[1]
    result_json = dumps(result_dict)
    return result_json
  except Exception as e:
    logger.error("Failed to get listings page {}".format(e))
    return jsonify(success=False,
      message='Failed to get listings page')

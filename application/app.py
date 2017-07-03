# -*- coding: utf-8 -*-
from .models import City
from index import app, db
from .utils.helper import uuid_gen, json_validate, requires_auth
from .utils.query import QueryHelper
from flask import request, jsonify
import json

logger = app.logger

@app.route('/api/index_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_auth
def index_page():
  columns = ['rental_radio', 'house_price_trend', 'increase_radio', 'rental_income_radio']
  d = {}
  try:
    index_page = QueryHelper.get_index_page()
    index_page.rental_radio = json.loads(index_page.rental_radio)
    index_page.house_price_trend = json.loads(index_page.house_price_trend)
    index_page.increase_radio = json.loads(index_page.increase_radio)
    index_page.rental_income_radio = json.loads(index_page.rental_income_radio)
    d['index_page'] = index_page
  except Exception as e:
    logger.error("Failed to get index page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get index page list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/get_cities', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_auth
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
@requires_auth
def city_page():
  columns = ['sale_online_offline', 'rent_online_offline', 'house_sale_number', 'house_rent_number',
    'block_villa_max', 'block_villa_min', 'block_apartment_max', 'block_apartment_min', 'one_room_one_toilet',
    'two_room_two_tiolet', 'three_room_two_tiolet', 'rental_radio', 'house_price_trend', 'increase_radio',
    'rental_income_radio', 'list_average_price', 'deal_average_price']
  d = {}
  try:
    incoming = request.get_json()
    city_page = QueryHelper.get_city_page_with_city_id(city_id=incoming['city_id'])
    city_page.rent_online_offline = json.loads(city_page.rent_online_offline)
    city_page.sale_online_offline = json.loads(city_page.sale_online_offline)
    city_page.house_price_trend = json.loads(city_page.house_price_trend)
    d['city_page'] = city_page
  except Exception as e:
    logger.error("Failed to get city page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get city page list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/api/home_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['home_id', 'token'])
@requires_auth
def home_page():
  columns = ['map_box_place_name', 'score', 'house_price_dollar', 'house_price_dollar', 'exchange_rate',
    'rent', 'size', 'bedroom', 'bathroom', 'rental_radio', 'increase_radio', 'rental_income_radio', 'furture_increase_radio',
    'house_price_trend']
  d = {}
  try:
    incoming = request.get_json()
    home_page = QueryHelper.get_home_page_with_home_id(home_id=incoming['home_id'])
    d['neighborhood_trend'] = json.loads(home_page.neighborhood.house_price_trend)
    d['city_trend'] = json.loads(home_page.neighborhood.city.citypage.house_price_trend)
    home_page.house_price_trend = json.loads(home_page.house_price_trend)
    d['home_page'] = home_page
  except Exception as e:
    logger.error("Failed to get home page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get home page list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/ping', methods=['GET'])
def ping():
  return 'pong'
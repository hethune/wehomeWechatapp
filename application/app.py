# -*- coding: utf-8 -*-
from .models import City
from index import app, db
from .utils.helper import uuid_gen, json_validate, requires_auth
from .utils.query import QueryHelper
from flask import request, jsonify

logger = app.logger

@app.route('/api/index_page', methods=['POST'])
@uuid_gen
@json_validate(filter=['token'])
@requires_auth
def index_page():
  columns = ['house_purchase_quantity', 'rental_radio', 
    'house_price_trend', 'increase_radio', 'rental_income_radio']
  d = {}
  try:
    index_page = QueryHelper.get_index_page()
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
  columns = ['city_id', 'house_sale_number', 'house_rent_number', 'house_price_max', 
    'house_price_median', 'house_price_min', 'house_rent_max', 'house_rent_min', 'one_room',
    'two_room', 'three_room', 'rental_radio', 'house_price_trend', 'increase_radio', 'rental_income_radio']
  d = {}
  try:
    incoming = request.get_json()
    city_page = QueryHelper.get_city_page_with_city_id(city_id=incoming['city_id'])
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
  columns = ['score', 'house_price_dollar', 'house_price_rmb',
    'rent', 'size', 'bedroom', 'bathroom', 'rental_radio', 'increase_radio',
    'rental_income_radio']
  d = {}
  try:
    incoming = request.get_json()
    home_page = QueryHelper.get_home_page_with_home_id(home_id=incoming['home_id'])
    d['home_page'] = home_page
  except Exception as e:
    logger.error("Failed to get home page list {}".format(e))
    return jsonify(success=False,
      message='Failed to get home page list')
  return QueryHelper.to_json_with_filter(rows_dict=d, columns=columns)

@app.route('/ping', methods=['GET'])
def ping():
  return 'pong'
from ..models import City, IndexPage, CityPage, HomePage, UnmatchedPlace
from index import app, db
from flask import jsonify
from sqlalchemy import and_
import hashlib

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
  def get_unmatched_place(cls, place_name):
    return UnmatchedPlace.query.filter_by(place_name=place_name).first()

  @classmethod
  def add_unmatched_place(cls, place_name):
    place = cls.get_unmatched_place(place_name)
    if place:
      return True
    try:
      place = UnmatchedPlace(place_name=place_name)
      db.session.add(place)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def parse_address_by_map_box(cls, place_name):
    try:
      releveance = 0.9
      url = "https://api.tiles.mapbox.com/geocoding/v5/mapbox.places/{address}.json".format(address=quote_plus(place_name))
      querystring = {"country":"us","limit":"1","access_token": app.config['MAP_BOX_ACCESSTOKEN']}
      headers = {
          'cache-control': "no-cache",
          }
      response = requests.request("GET", url, headers=headers, params=querystring, proxies=None)
      result = json.loads(response.text)
      
      if len(result['features'])>0 and result['features'][0]['relevance']>= releveance:
        return result['features'][0]['place_name']
    except Exception:
      return place_name
    return place_name
from ..models import City, IndexPage, CityPage, HomePage
from flask import jsonify

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
from index import db
# from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
import datetime

class City(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  city_name = db.Column(db.String(255), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

class IndexPage(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  house_purchase_quantity = db.Column(db.Integer())
  rental_radio = db.Column(db.Float())
  house_price_trend = db.Column(db.Text())
  increase_radio = db.Column(db.Text())
  rental_income_radio = db.Column(db.Text())
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

class CityPage(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  city_id = db.Column(db.Integer(), db.ForeignKey("city.id"), index=True, nullable=False)
  house_sale_number = db.Column(db.Integer())
  house_rent_number = db.Column(db.Integer())
  house_price_max = db.Column(db.Float())
  house_price_median = db.Column(db.Float())
  house_price_min = db.Column(db.Float())
  house_rent_max = db.Column(db.Float())
  house_rent_min = db.Column(db.Float())
  one_room = db.Column(db.Float())
  two_room = db.Column(db.Float())
  three_room = db.Column(db.Float())
  rental_radio = db.Column(db.Float())
  house_price_trend = db.Column(db.Text())
  increase_radio = db.Column(db.Text())
  rental_income_radio = db.Column(db.Text())
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

class HomePage(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  city_id = db.Column(db.Integer(), db.ForeignKey("city.id"), index=True, nullable=False)
  source_id = db.Column(db.String(255), index=True)
  score = db.Column(db.Float())
  house_price_dollar = db.Column(db.Float())
  house_price_rmb = db.Column(db.Float())
  rent = db.Column(db.Float())
  size = db.Column(db.Integer())
  bedroom = db.Column(db.Integer())
  bathroom = db.Column(db.Float())
  rental_radio = db.Column(db.Float())
  increase_radio = db.Column(db.Float())
  rental_income_radio = db.Column(db.Float())
  furture_increase_radio = db.Column(db.Float())
  house_price_trend = db.Column(db.Text())
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
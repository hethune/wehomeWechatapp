from index import db
# from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
import datetime

class City(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  city_name = db.Column(db.String(255), index=True)
  eng_name = db.Column(db.String(255), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
  # neighborhoods = relationship("Neighborhood", back_populates="city")
  homepages = relationship("HomePage", back_populates="city")
  citypage = relationship("CityPage", back_populates="city", uselist=False)

class Neighborhood(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  neighbor_name = db.Column(db.Text())
  neighbor_rental_radio = db.Column(db.Float())
  house_price_trend = db.Column(db.Text())
  neighborhood_score = db.Column(db.Float(), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
  homepages = relationship("HomePage", back_populates="neighborhood")

class IndexPage(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  rental_radio = db.Column(db.Text())
  house_price_trend = db.Column(db.Text())
  increase_radio = db.Column(db.Text())
  exchange_rate = db.Column(db.Float())
  rental_income_radio = db.Column(db.Text())
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

class CityPage(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  city_id = db.Column(db.Integer(), db.ForeignKey("city.id", ondelete="CASCADE"), index=True, nullable=False, unique=True)
  sale_online_offline = db.Column(db.Text())
  rent_online_offline = db.Column(db.Text())
  house_sale_number = db.Column(db.Integer())
  house_rent_number = db.Column(db.Integer())
  block_villa_max = db.Column(db.Float())
  block_villa_median = db.Column(db.Float())
  block_villa_min = db.Column(db.Float())
  list_average_price = db.Column(db.Float())
  deal_average_price = db.Column(db.Float())
  block_apartment_max = db.Column(db.Float())
  block_apartment_median = db.Column(db.Float())
  block_apartment_min = db.Column(db.Float())
  one_room_one_toilet = db.Column(db.Text())
  two_room_two_toilet = db.Column(db.Text())
  three_room_two_toilet = db.Column(db.Text())
  rental_radio = db.Column(db.Float())
  house_price_trend = db.Column(db.Text())
  increase_radio = db.Column(db.Float())
  rental_income_radio = db.Column(db.Float())
  one_bed_one_bath_lower_bound = db.Column(db.Integer())
  one_bed_one_bath_upper_bound = db.Column(db.Integer())
  two_bed_two_bath_lower_bound = db.Column(db.Integer())
  two_bed_two_bath_upper_bound = db.Column(db.Integer())
  three_bed_two_bath_lower_bound = db.Column(db.Integer())
  three_bed_two_bath_upper_bound = db.Column(db.Integer())
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
  city = relationship("City", back_populates="citypage")

class HomePage(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  neighbor_id = db.Column(db.Integer(), db.ForeignKey("neighborhood.id", ondelete="CASCADE"), index=True, nullable=False)
  city_id = db.Column(db.Integer(), db.ForeignKey("city.id", ondelete="CASCADE"), index=True)
  source_id = db.Column(db.String(255), index=True)
  source = db.Column(db.String(255), index=True)
  map_box_place_name = db.Column(db.Text())
  address = db.Column(db.Text(), index=True)
  score = db.Column(db.Float())
  house_price_dollar = db.Column(db.Float())
  rent = db.Column(db.Float())
  size = db.Column(db.Integer())
  bedroom = db.Column(db.Integer())
  bathroom = db.Column(db.Float())
  rental_radio = db.Column(db.Float(), index=True)
  increase_radio = db.Column(db.Float())
  rental_income_radio = db.Column(db.Float())
  longitude = db.Column(db.Float())
  latitude = db.Column(db.Float())
  # md5 hash code for map_box_place_name
  hash_code = db.Column(db.CHAR(32), index=True)
  # which step back fill in
  step = db.Column(db.Integer(), default=0, index=True)
  adjust_score = db.Column(db.Float(), index=True)
  property_score = db.Column(db.Float(), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
  neighborhood = relationship("Neighborhood", back_populates="homepages")
  city = relationship("City", back_populates="homepages")
  collections = relationship("Collection", back_populates="homepage")

  __table_args__ = (
    db.Index("idx_longitude_latitude", "longitude", "latitude"),
  )

class UnmatchedPlace(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  place_name = db.Column(db.Text(), index=True)
  # one of ['map_box_place_name', 'score', 'house_price_dollar', 'exchange_rate',
  #  'rent', 'rental_radio', 'increase_radio', 'rental_income_radio',
  #  'neighborhood_rent_radio', 'city_name', 'city_trend', 'neighborhood_trend']
  type = db.Column(db.String(64), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

  def __init__(self, place_name, type):
    self.place_name = place_name
    self.type = type

  __table_args__ = (
    db.Index("idx_place_name_type", "place_name", "type"),
  )

class FeedBack(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  user_id = db.Column(db.Integer(), db.ForeignKey("user.id", ondelete="CASCADE"), index=True)
  content = db.Column(db.Text(), index=True, nullable=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

  def __init__(self, content, user_id):
    self.content = content
    self.user_id = user_id

class User(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  phone = db.Column(db.String(255), index=True)
  openid = db.Column(db.String(64), index=True, unique=True)
  nick_name= db.Column(db.String(255))
  gender = db.Column(db.Integer)
  language = db.Column(db.String(255), index=True)
  city = db.Column(db.String(255), index=True)
  province = db.Column(db.String(255), index=True)
  country = db.Column(db.String(255), index=True)
  country_code = db.Column(db.String(16), index=True)
  avatar_url = db.Column(db.String(1024))
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

  def __init__(self, openid, nick_name, gender, language, city, province, country, avatar_url, phone=None):
    self.openid = openid
    self.nick_name = nick_name
    self.gender = gender
    self.language = language
    self.city = city
    self.province = province
    self.country = country
    self.avatar_url = avatar_url
    self.phone = phone

class Phone(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  phone = db.Column(db.String(255))
  country = db.Column(db.String(255))
  verification_code = db.Column(db.String(255))
  verification_code_created_at = db.Column(db.DateTime())
  is_verified = db.Column(db.Boolean(), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

  __table_args__ = (
    db.Index("idx_phone", "phone"),
    db.Index("idx_phone_country", "phone", "country"),
    db.UniqueConstraint("phone", "country", name='unique_phone_contry'),
  )

  def __init__(self, phone, country, verification_code, verification_code_created_at, is_verified=False):
    self.phone = phone
    self.country = country
    self.verification_code = verification_code
    self.verification_code_created_at = verification_code_created_at
    self.is_verified = is_verified

class Collection(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  user_id = db.Column(db.Integer(), db.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
  home_id = db.Column(db.Integer(), db.ForeignKey("home_page.id", ondelete="CASCADE"), index=True, nullable=False)
  is_active = db.Column(db.Boolean(), default=False)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
  homepage = relationship("HomePage", back_populates="collections")

  def __init__(self, user_id, home_id, is_active=True):
    self.user_id = user_id
    self.home_id = home_id
    self.is_active = is_active

  __table_args__ = (
    db.Index("idx_user_id_home_id", "user_id", "home_id"),
  )
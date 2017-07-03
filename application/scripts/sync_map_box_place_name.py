import requests
from urllib import quote_plus
import json
from sqlalchemy import text
from index import db 

def write_place_name_to_db(home_id, replace_name):
  query = '''
	UPDATE home_page 
	SET map_box_replace_name = {replace_name}
	WHERE
	    id = {home_id}
	'''.format(home_id=home_id, replace_name=replace_name)
    try:
      db.execute(text(query))
      db.commit()
    except Exception as:
      db.rollback()

def sync_by_address(home_id, address):
  url = "https://api.tiles.mapbox.com/geocoding/v5/mapbox.places/{address}.json".format(address=quote_plus(address))
  querystring = {"country":"us","limit":"1","access_token":"pk.eyJ1IjoidG1jdyIsImEiOiJIZmRUQjRBIn0.lRARalfaGHnPdRcc-7QZYQ"}
  headers = {
      'cache-control': "no-cache",
      }
  response = requests.request("GET", url, headers=headers, params=querystring)
  result = json.loads(response.text)
  if result['features'][0]['relevance']>= releveance:
    write_place_name_to_db(home_id=home_id, replace_name=replace_name) 

def sync_by_lang_lat(home_id, lang, lat):
  url = "https://api.mapbox.com/geocoding/v5/mapbox.places/{lang},{lat}.json".format(lang=lang, lat=lat)
  querystring = {"country":"us","limit":"1","access_token":"pk.eyJ1IjoidG1jdyIsImEiOiJIZmRUQjRBIn0.lRARalfaGHnPdRcc-7QZYQ"}
  headers = {
      'cache-control': "no-cache",
      }
  response = requests.request("GET", url, headers=headers, params=querystring)
  result = json.loads(response.text)
  write_place_name_to_db(home_id=home_id, replace_name=replace_name) 

if __name__ == '__main__':
  print'step one back-fill with place name'
  query = '''
	SELECT id, address 
	FROM	
	    home_page
	WHERE
	   address is not null
	AND
	   replace_name is not null
  '''
  #sync_by_address(address='41742 Osgood Rd yes')
  print 'tep two back-fill with lang and lat'
  query = '''
	SELECT id, address 
	FROM	
	    home_page
	WHERE
	   address is not null
	AND
	   longitude is not null
	AND
	   latitude is not null
  '''
  #sync_by_lang_lat(lang=-122.326272,lat=47.678353)

import time
import json
import requests
import configparser

# Read config file.
config = configparser.ConfigParser()
try:
        config.read('./config.ini')

except FileExistsError as err:
        print('File exists error: {0}', err)
        sys.exit(1)

city = config['Common']['city']
radius = config['PlacesAPI']['radius']
apikey = config['PlacesAPI']['apikey']
coordinate = config['PlacesAPI']['coordinate']

class GooglePlaces(object):
    def __init__(self, apiKey):
        super(GooglePlaces, self).__init__()
        self.apiKey = apiKey

    def search_places_by_coordinate(self, coordinate, radius, types):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        places = []
        params = {
            'location': coordinate,
            'radius': 4000,
            #'types': types,
            'key': self.apiKey
        }
        res = requests.get(endpoint_url, params = params)
        results =  json.loads(res.content)
        places.extend(results['results'])
        time.sleep(2)
        while "next_page_token" in results:
            params['pagetoken'] = results['next_page_token'],
            res = requests.get(endpoint_url, params = params)
            results = json.loads(res.content)
            places.extend(results['results'])
            time.sleep(2)
        return places

    def get_place_details(self, place_id, fields):
        endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            'placeid': place_id,
            'fields': ",".join(fields),
            'key': self.apiKey
        }
        res = requests.get(endpoint_url, params = params)
        place_details =  json.loads(res.content)
        return place_details

if __name__ == '__main__':
	api = GooglePlaces(apikey)
	places = api.search_places_by_coordinate(coordinate, radius, "restaurant")
	fields = ['name', 'formatted_address', 'international_phone_number', 'website', 'rating', 'review']
	websites = []
	placesarr = []
	for place in places:
		placesarr.append(place['place_id'])
		details = api.get_place_details(place['place_id'], fields)
		try:
			website = details['result']['website']
			websites.append(website)
			print(website)
		except KeyError:
			website = ""
	print(websites)
	print("Numero de webs",len(websites))
	print(placesarr)
	print("Numero de places",len(placesarr))

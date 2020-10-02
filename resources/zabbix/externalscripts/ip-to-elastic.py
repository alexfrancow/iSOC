import sys
import hashlib
import argparse
from elasticsearch import Elasticsearch, helpers
import pgeocode
import geoip2
import geoip2.webservice
import geoip2.database
import datetime
import warnings
warnings.filterwarnings("ignore")

es = Elasticsearch([{'host':'htc001.blackbrains.org','port':9200}])
INDEX_NAME = "htc"

if es.indices.exists(INDEX_NAME):
        print()

else:
        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        res = es.indices.create(index='htc', ignore=400)

nomi = pgeocode.Nominatim('es')
reader = geoip2.database.Reader('GeoLite2-City.mmdb')

parser = argparse.ArgumentParser(description='Discover WordPress version with Machine Learning')
parser.add_argument('-i', '--ip', help='IP address to scan', type=str, action="store")
args = parser.parse_args()

if args.ip:
    elastic_docs = []
    ip = args.ip
    response = reader.city(ip)
    hash_object = hashlib.md5(ip.encode())
    md5_hash = hash_object.hexdigest()
    doc = {}
    doc["_id"] = md5_hash
    doc['ip'] = ip
    doc['time_added'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc['zip_code'] = response.postal.code
    lat = nomi.query_postal_code(response.postal.code)["latitude"]
    lng = nomi.query_postal_code(response.postal.code)["longitude"]
    doc['location'] = [lng,lat]
    doc['lat'] = lat
    doc['lng'] = lng
    doc['place_name'] = nomi.query_postal_code(response.postal.code)["place_name"]
    doc['network'] = response.traits.network.with_prefixlen
    doc['city'] = response.city.name
    doc['iso_code'] = response.country.iso_code
    elastic_docs += [doc]
    result = helpers.bulk(es, elastic_docs, index="htc", doc_type="_doc")
    #print(result['created'])
    #print ("helpers.bulk() RESPONSE:", json.dumps(resp, indent=4))
    sys.exit()
else:
    sys.exit()

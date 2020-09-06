'''
        Script to generate data and insert it into the mongoDB.
                @alexfrancow
        https://kb.objectrocket.com/elasticsearch/how-to-bulk-index-elasticsearch-documents-from-a-json-file-using-python-753
'''

import pgeocode
import datetime
import subprocess
import os.path
import pymongo
import configparser
import json
from elasticsearch import Elasticsearch, helpers
from utils import mask_to_hosts, city_range, hosts_up
import geoip2
import geoip2.webservice
import geoip2.database

es = Elasticsearch([{'host':'192.168.1.129','port':9200}])
INDEX_NAME = "isoc"

"""
mappings = {
"mappings": {
        "properties": {
            "location": {"type": "geo_point"},
            "lat": {"type": "geo_point"},
            "lng": {"type": "geo_point"}
        }
}}
"""

# http://192.168.1.129:9200/isoc/_mappings ?"ports_w_protocol":{"type":"nested"}?
mappings =  {"mappings":{"properties":{"city":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"host_up":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"ip":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"iso_code":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"lat":{"type":"float"},"lng":{"type":"float"},"location":{"type":"geo_point"},"network":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"place_name":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"technologies_w_version":{"type":"object"},"time_added":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"web_headers":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"web_payload":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}},"zip_code":{"type":"text","fields":{"keyword":{"type":"keyword","ignore_above":256}}}}}}

if es.indices.exists(INDEX_NAME):
        sure = input("Do you want delete the current DB? [Y/n]: ").lower()
        if sure == "" or "y" in sure:
                print("deleting '%s' index..." % (INDEX_NAME))
                res = es.indices.delete(index = INDEX_NAME)
                print(" response: '%s'" % (res))
                res = es.indices.create(index='isoc', body=mappings, ignore=400)
        else:
                print()

else:
        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        res = es.indices.create(index='isoc', body=mappings, ignore=400)
        print(res)


# Read config file.
config = configparser.ConfigParser()
try:
        config.read('./config.ini')

except FileExistsError as err:
        print('File exists error: {0}', err)
        sys.exit(1)

city = config['Common']['city']
location = config['pgeocode']['location']

nomi = pgeocode.Nominatim(location)

# Servers from GeoLite2
reader = geoip2.database.Reader('data/maxmind/GeoLite2-City.mmdb')

if not os.path.isfile('ips_arr.txt'):
        print("[i] Getting IPs from maxmind database")
        IPS = hosts_up(city)
        print(IPS)

        with open("ips_arr.txt", "w") as f:
                f.write(str(IPS))

else:
        with open("ips_arr.txt", "r") as f:
                IPS = f.read()
        content_list = IPS.replace(" ", "").replace("'", "").replace("\n", "").split(",")
        elastic_docs = []
        for num, ip in enumerate(content_list):
                print("Adding some IPs:", ip, end="\r", flush=True)
                response = reader.city(ip)
                doc = {}
                doc["_id"] = num
                doc['ip'] = ip
                #nslookup = str(subprocess.check_output('nslookup '+ip+' | head -1 | cut -d "=" -f 2',
                #                               shell=True)).replace(" ","")
                #doc['name'] = nslookup
                doc['time_added'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                doc['host_up'] = "Yes"
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
                doc['ports'] = []
                doc['ports_w_protocol'] = {}
                doc['technologies'] = []
                doc['technologies_w_version'] = {}
                doc['web_payload'] = ""
                doc['web_headers'] = ""
                doc['subdomains'] = []
                elastic_docs += [doc]

        result = helpers.bulk(es, elastic_docs, index="isoc", doc_type="_doc")
        print(result['created'])
        print ("helpers.bulk() RESPONSE:", json.dumps(resp, indent=4))


# Servers from placesAPI (Google)
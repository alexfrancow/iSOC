'''
        Script to generate data and insert it into the mongoDB.
                @alexfrancow
'''

import pgeocode
import datetime
import subprocess
import os.path
import pymongo
import configparser
from pymongo import MongoClient
from utils import mask_to_hosts, city_range, hosts_up
import geoip2
import geoip2.webservice
import geoip2.database

client = MongoClient()
client = MongoClient('localhost',
                        username="alexfrancow",
                        password="abc123",
                        )


# Check DB exists
dblist = client.list_database_names()
if "iSOC" in dblist:
        print("The database exists.")

# Use iSOC DB
mydb = client["iSOC"]
for db in client.list_databases():
    print(db)

# Check Collection exists
collist = mydb.list_collection_names()
if "assets" in collist:
        print("The collection exists.")

# Use assets collection
mycol = mydb["assets"]

for coll in mydb.list_collection_names():
    print("List of collections:", coll)


# Drop previous collections
sure = input("Do you want delete the current DB? [Y/n]: ").lower()
if sure == "" or "y" in sure:
        print("Deleting DB")
        mycol.drop()
else:
        print()

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
        mongo_docs = []
        for num, ip in enumerate(content_list):
                print("Adding some IPs:", ip, end="\r", flush=True)
                response = reader.city(ip)
                doc = {}
                doc['ip'] = ip
                #nslookup = str(subprocess.check_output('nslookup '+ip+' | head -1 | cut -d "=" -f 2',
                #                               shell=True)).replace(" ","")
                #doc['name'] = nslookup
                doc['time_added'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                doc['host_up'] = "Yes"
                doc['zip_code'] = response.postal.code
                doc['lat'] = nomi.query_postal_code(response.postal.code)["latitude"]
                doc['lng'] = nomi.query_postal_code(response.postal.code)["longitude"]
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
                mongo_docs += [doc]

        result = mycol.insert_many(mongo_docs)
        total_docs = len(result.inserted_ids)
        print ("total inserted:", total_docs)
        print ("inserted IDs:", result.inserted_ids, "\n\n")

# Servers from placesAPI (Google)

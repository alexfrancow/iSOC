# -*- coding: utf-8 -*-

import subprocess
from subprocess import check_output
import requests
import time
import argparse
import configparser
import re
import os
import json
import sys
import glob
import threading
from multiprocessing import Pool
import concurrent.futures
from utils import mask_to_hosts, city_range, hosts_up

from pyzabbix import ZabbixAPI
import geoip2
import geoip2.webservice
import geoip2.database
import pandas as pd
import numpy as np


parser = argparse.ArgumentParser(description='PONER DESCRIPCION')
parser.add_argument('-d', '--dataset', help='Only adds a new city into ZABBIX', type=str, action="store")
args = parser.parse_args()
threadLocal = threading.local()

def get_session():
	if not hasattr(threadLocal, "session"):
		threadLocal.session = requests.Session()
	return threadLocal.session


def kibana_create_openvas_index(kibana_ip):
	headers = {
    		'Content-Type': 'application/json',
    		'kbn-xsrf': 'anything',
	}

	data = '{"attributes":{"title":"logstash-*"}}'
	requests.post(kibana_ip+'/api/saved_objects/index-pattern/logstash-*', headers=headers, data=data)


def zabbix_upload_templates():
	rules = {
		'applications': {
			'createMissing': True,
		},
		'discoveryRules': {
			'createMissing': True,
			'updateExisting': True
		},
		'graphs': {
			'createMissing': True,
			'updateExisting': True
		},
		'groups': {
			'createMissing': True
		},
		'hosts': {
			'createMissing': True,
			'updateExisting': True
		},
		'images': {
			'createMissing': True,
			'updateExisting': True
		},
		'items': {
			'createMissing': True,
			'updateExisting': True
		},
		'maps': {
			'createMissing': True,
			'updateExisting': True
		},
		'screens': {
			'createMissing': True,
			'updateExisting': True
		},
		'templateLinkage': {
			'createMissing': True,
		},
		'templates': {
			'createMissing': True,
			'updateExisting': True
		},
		'templateScreens': {
			'createMissing': True,
			'updateExisting': True
		},
		'triggers': {
			'createMissing': True,
			'updateExisting': True
		},
		'valueMaps': {
			'createMissing': True,
			'updateExisting': True
		},
	}

	files = glob.glob('resources/zabbix/templates/*.xml')
	for file in files:
		print("    "+file)
		with open(file, 'r') as f:
			template = f.read()
			try:
				zapi.confimport('xml', template, rules)
			except ZabbixAPIException as e:
				print(e)



def zabbix_create_actions():
	headers = {
		'Content-type': 'application/json',
	}

	data = '{"jsonrpc":"2.0","method":"user.login","params":{ "user":"Admin","password":"zabbix"},"auth":null,"id":0}'
	response = requests.post('http://127.0.0.1/api_jsonrpc.php', headers=headers, data=data)
	response = response.json()
	token = response.get("result", )

	files = glob.glob('resources/zabbix/actions/*.json')
	for file in files:
		print("    "+file)
		with open(file, 'r') as f:
			data = json.load(f)
			data['auth'] = token

			response = requests.post('http://127.0.0.1/api_jsonrpc.php', headers=headers, data=json.dumps(data))
			print(response.json())

def zabbix_create_host(ip):
	session = get_session()
	print("    "+ip)
	get__templates = zapi.template.get(output=['templateid', 'name'])
	for template in get__templates:
		if "Template App Service Ports" in template.get("name", ):
			templateidports = template.get("templateid", )
		if template.get("name", ) == "Main":
			templateidmain = template.get("templateid", )

	"""
	host = zapi.host.create(
		host=ip,
		groups=[5],
		templates=templateid,
		interfaces=[{"type":2,"main":1,"useip":1,"ip":ip}],
	)
	"""

	headers = {
		'Content-type': 'application/json',
	}

	data = '{"jsonrpc":"2.0","method":"user.login","params":{ "user":"Admin","password":"zabbix"},"auth":null,"id":0}'
	response = requests.post('http://127.0.0.1/api_jsonrpc.php', headers=headers, data=data)
	response = response.json()
	token = response.get("result", )

	data = '{"jsonrpc": "2.0","method": "host.create","params": {"host": "'+ip+'","interfaces": [{"type": 2,"main": 1,"useip": 1,"ip": "'+ip+'","dns": "","port": "10050"}],"groups": [{"groupid": "5"}],"templates": [{"templateid":"'+templateidports+'"}, {"templateid":"'+templateidmain+'"}],"macros": [{"macro": "{$USER_ID}","value": "123321"}],"inventory_mode": 0,"inventory": {"macaddress_a": "01234","macaddress_b": "56768"}},"auth": "'+token+'","id": 1}'
	response = requests.post('http://127.0.0.1/api_jsonrpc.php', headers=headers, data=data)
	response = response.json()


def zabbix_create_host_multiple(ips):
	with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        	df = pd.concat(executor.map(zabbix_create_host, ips))
	return df

def requirements():
	cmd = ["apt", "list", "--installed"]
	out = check_output(cmd)
	if "masscan" in str(out):
		print("    [*] Masscan OK")


def zabbix_requirements():
	os.system("docker exec zabbix apk update && docker exec zabbix apk add nmap && docker exec zabbix apk add py-pip && docker exec zabbix pip install openvas-lib")

# Read config file.
config = configparser.ConfigParser()
try:
	config.read('./config.ini')

except FileExistsError as err:
        print('File exists error: {0}', err)
        sys.exit(1)

city = config['Common']['city']
zabbix_ip = config['Zabbix']['ip']
zabbix_username = config['Zabbix']['username']
zabbix_password = config['Zabbix']['password']
kibana_ip = config['Elk']['kibana_ip']


print("[i] Checking requirements..")
requirements()

# Iniciar contenedores
#subprocess.call(["docker-compose", "up"])

while True:
	print("[i] Waiting for zabbix to be up..")
	try:
		response = requests.get(zabbix_ip)
		if "zabbix" in response.content.decode('utf-8'):
			print("    [*] Zabbix is up!")
			print("    [*] Installing requirements")
			zabbix_requirements()
			break

	except:
		pass
	time.sleep(5)


while True:
	print("[i] Waiting for kibana to be up..")
	try:
		response = requests.get(kibana_ip)
		if "kibanaLoaderWrap" in response.content.decode('utf-8'):
			print("    [*] Kibana is up!")
			break

	except:
		pass

	time.sleep(5)


zapi = ZabbixAPI(zabbix_ip)
zapi.login(zabbix_username, zabbix_password)

print("[i] Importing templates..")
zabbix_upload_templates()

print("[i] Importing actions..")
zabbix_create_actions()

print("[i] Creating openvas index in Kibana..")
kibana_create_openvas_index(kibana_ip)

print("[i] Getting list of servers from mongoDB..")
client = MongoClient("localhost",
		username="alexfrancow",
		password="abc123",
		maxPoolSize=50)
db = client.iSOC
collection = db['assets']
cursor = collection.find({})

count = 0
IPS = []
for document in cursor:
	count += 1
	IPS.append(document['ip'])
print("[i] Total servidores: ", count)


print("[i] Importing hosts..")
#IPS = ['192.168.1.13', '217.127.74.13', '217.127.75.235', '217.127.74.95', '217.127.75.110', '217.127.75.107', '217.127.74.86', '217.127.75.189', '217.127.75.186', '217.127.74.248', '217.127.75.77', '217.127.74.143', '217.127.75.126']
zabbix_create_host_multiple(IPS)

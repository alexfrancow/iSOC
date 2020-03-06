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
import threading
import glob

from pyzabbix import ZabbixAPI
import geoip2
import geoip2.webservice
import geoip2.database
import pandas as pd
import numpy as np


parser = argparse.ArgumentParser(description='PONER DESCRIPCION')
parser.add_argument('-d', '--dataset', help='Only adds a new city into ZABBIX', type=str, action="store")
args = parser.parse_args()


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


def requirements():
	cmd = ["apt", "list", "--installed"]
	out = check_output(cmd)
	if "masscan" in str(out):
		print("    [*] Masscan OK")


def zabbix_requirements():
	os.system("docker exec zabbix apk update && docker exec zabbix apk add nmap && docker exec zabbix apk add py-pip && docker exec zabbix pip install openvas-lib")

def mask_to_hosts(mask):
    if mask == '24':
        return '254'
    elif mask == '22':
        return '1022'
    elif mask == '23':
        return '510'
    elif mask == '25':
        return '126'
    elif mask == '26':
        return '62'
    elif mask == '29':
        return '6'
    elif mask == '28':
        return '14'
    elif mask == '27':
        return '30'
    elif mask == '21':
        return '2046'
    elif mask == '20':
        return '4094'


def city_range(city):
    reader = geoip2.database.Reader('data/maxmind/GeoLite2-City.mmdb')
    df = pd.read_csv('data/maxmind/GeoLite2-City-Blocks-IPv4.csv')

    dff = pd.DataFrame({'city': [], 'range_ips': [], 'range_ips_mask': [], 'hosts': []})
    for col in df['network']:
        col = col.split('/')
        response = reader.city(col[0])

        if response.city.name:
            if city in response.city.name:
                print("[*] Adding IP: ", col[0])
                dff = dff.append(pd.DataFrame({'city': [response.city.name], 'range_ips': [col[0]], 'range_ips_mask' : [col[0] + '/' + col[1]], 'hosts': [str(mask_to_hosts(col[1]))]}), ignore_index=True)
            else:
                pass
        else:
            pass

    reader.close()

    print("[i] Saving IPs into " + city +".csv")
    dff.to_csv('data/maxmind/'+city+'.csv')
    return dff


def hosts_up(city):
    df = city_range(city)
    masscan_rate = "100000"
    count = 0
    ips = []
    for col in df['range_ips_mask']:
        cmd = ["masscan", col, "--ping", "--wait", "0", "--max-rate", masscan_rate]
        print(cmd)
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE, encoding="utf-8")
        for line in out.stdout.readlines():
            if "Discovered open port 0/icmp on" in line:
                ip = line.split(" ")[5]
                print("[*] Host alive: ", ip)
                ips.append(ip)
                count += 1
            else:
                continue

    print(str(count))
    return ips


# Read config file.
config = configparser.ConfigParser()
try:
	config.read('./config.ini')

except FileExistsError as err:
        print('File exists error: {0}', err)
        sys.exit(1)


city = config['Common']['city']
zabbix_ip = config['Zabbix']['ip']


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

	except ValueError as e:
		print(e)
		pass

	time.sleep(5)

zapi = ZabbixAPI(zabbix_ip)
zapi.login("Admin", "zabbix")

print("[i] Importing templates..")
zabbix_upload_templates()

print("[i] Importing actions..")
zabbix_create_actions()

print("[i] Getting IPs from maxmind database")
#ips = hosts_up(city)
#print(ips)


print("[i] Importing hosts..")
IPS = ['192.168.1.13', '217.127.74.13', '217.127.75.235', '217.127.74.95', '217.127.75.110', '217.127.75.107', '217.127.74.86', '217.127.75.189', '217.127.75.186', '217.127.74.248', '217.127.75.77', '217.127.74.143', '217.127.75.126']
for IP in IPS:
	print("    "+IP)
	zabbix_create_host(IP)


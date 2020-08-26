'''
	List of functions used by the app.
		@alexfrancow
'''


import subprocess
import pandas as pd
import geoip2
import geoip2.webservice
import geoip2.database
import numpy as np


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


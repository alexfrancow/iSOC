# iSOC 

Deploy an "illegal" SOC (Security Operations Center) to audit all the servers in your city in a few minutes. 

[![](https://img.shields.io/badge/twitter-@alexfrancow-00aced?style=flat-square&logo=twitter&logoColor=white)](https://twitter.com/alexfrancow) [![](https://img.shields.io/badge/linkedin-@alexfrancow-0084b4?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/alexfrancow) [![](https://img.shields.io/badge/linkedin-@jlopezprado-0084b4?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jlopezprado/)

## Requirements

Tested on:
- Debian 10
- Docker-compose version 1.25.4, build 8d51620a
- Docker 19.03.6
- Python 3.7.3

```bash
$ sudo apt update
# Docker
$ sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common
$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
$ sudo apt update
$ apt-cache policy docker-ce
$ sudo apt install docker-ce
$ sudo systemctl status docker
$ sudo usermod -aG docker ${USER}
$ su - ${USER}
$ id -nG
$ sudo usermod -aG docker username
$ docker -v
# Docker-compose
$ curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ chmod +x /usr/local/bin/docker-compose
$ ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
$ docker-compose --version
# Python libraries
$ apt install python3-pip
$ pip3 install -r requirements.txt
# Virtual memory to Elasticsearch
$ sysctl -w vm.max_map_count=262144
```


## Getting started

```bash
$ python3 Main.py
[i] Checking requirements..
[i] Starting containers..
[i] Logs: $ docker-compose logs -f
Creating network "isoc_esnet" with the default driver
Creating network "isoc_default" with the default driver
Creating elk           ... done
Creating openvas       ... done
Creating zabbix        ... done
Creating vulnwhisperer ... done
[i] Waiting for zabbix to be up..
    [*] Zabbix is up!
    [*] Installing requirements
[i] Waiting for kibana to be up..
    [*] Kibana is up!
[i] Importing templates..
    resources/zabbix/templates/template_app_service_ports.xml
    resources/zabbix/templates/main-template.xml
[i] Importing actions..
    resources/zabbix/actions/run-scan-port-80.json
[i] Creating openvas index..
[i] Getting IPs from maxmind database
[i] Importing hosts..
    192.168.1.13
    ...
```

## Options

If you want to import a new template, you can place it in "resources/zabbix/templates/".


## Troubleshooting

### Scan reports

<p align="center"><img src="images/vulnwhisperer.jpg" height="400" width="625" /></p>

To launch an openvas report conversion manually, we will start the vulnwhisperer container:

```bash
$ docker-compose up vulnwhisperer
Starting vulnwhisperer ... done
Attaching to vulnwhisperer
vulnwhisperer       | WARNING: No section was specified, vulnwhisperer will scrape enabled modules from config file.
vulnwhisperer       | Please specify a section using -s.
vulnwhisperer       | Example vuln_whisperer -c config.ini -s nessus
vulnwhisperer       | INFO:root:main:No section was specified, vulnwhisperer will scrape enabled modules from the config file.
vulnwhisperer       | INFO:vulnWhispererBase:__init__:Connected to database at /opt/VulnWhisperer/data/database/report_tracker.db
vulnwhisperer       | INFO:vulnWhispererOpenVAS:directory_check:Directory already exist for /opt/VulnWhisperer/data/ - Skipping creation
vulnwhisperer       | INFO:OpenVAS_API:get_reports:Retreiving OpenVAS report data...
vulnwhisperer       | INFO:OpenVAS_API:get_report_formats:Retrieving available report formats
vulnwhisperer       | INFO:vulnWhispererOpenVAS:identify_scans_to_process:Identified 3 scans to be processed
vulnwhisperer       | INFO:vulnWhispererOpenVAS:process_openvas_scans:Processing 1/3 - Report ID: e3326680-afef-4292-897e-775a35dc6dba
```

The ELK container has shared the file 'resources/vulnwhisperer/vulnmod_logstash.conf' which is in charge of parsing the .json from the openvas report, to verify that this file is in the ELK container, we start the container interactively:

```bash
$ docker exec -it elk bash
$ vi /etc/logstash/conf.d/vulnmod_logstash.conf
	input {
  	    file {
  		path => "/opt/VulnWhisperer/data/*.json"
```

If we make an 'ls' of that folder we have to see our reports.

```bash 
$ ls /opt/VulnWhisperer/data/*.json
/opt/VulnWhisperer/data/openvas_scan_25826d5a471c444e941f942a771537f6_1584732168.json
/opt/VulnWhisperer/data/openvas_scan_5b0204d06b3d4a469389acb4ba4f6b31_1584647458.json
/opt/VulnWhisperer/data/openvas_scan_e3326680afef4292897e775a35dc6dba_1584647468.json
```

We can see in kibana how the data has been parsed with a previously created index:

```bash
logstash-vulnwhisperer-*
```

### Zabbix Discover:

```bash
$ docker ps
$ docker logs -f zabbix | grep discover
```

### Openvas NVT:

```bash
$ docker ps
$ docker logs -f openvas
```

## Errors

If you get an openvas login error when it starts, you must delete the 'volumes/openvas' directory.


## Documentation

- ELK https://elk-docker.readthedocs.io/
- OpenVas https://hub.docker.com/r/mikesplain/openvas/dockerfile
- Zabbix https://www.zabbix.com/documentation/current/manual

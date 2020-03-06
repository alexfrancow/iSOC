# iSOC 

Deploy an "illegal" SOC (Security Operations Center) to audit all the servers in your city in a few minutes. 

[![](https://img.shields.io/badge/twitter-@alexfrancow-00aced?style=flat-square&logo=twitter&logoColor=white)](https://twitter.com/alexfrancow) [![](https://img.shields.io/badge/linkedin-@alexfrancow-0084b4?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/alexfrancow)

## Requirements

Tested on:
- Debian 10
- Docker-compose version 1.25.4, build 8d51620a
- Docker 19.03.6
- Python 3.7.3

```bash
$ sudo apt update
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
$ curl -L "https://github.com/docker/compose/releases/download/1.25.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
$ chmod +x /usr/local/bin/docker-compose
$ ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
$ docker-compose --version
$ apt install python3-pip
$ pip3 install -r requirements.txt

```


## Getting started

```bash
$ docker-compose up
$ python Main.py
[i] Checking requirements.
    [*] Masscan OK
[i] Waiting for zabbix to be up..
    [*] Zabbix is up!
[i] Importing templates..
    resources/zabbix/templates/main-template.xml
    resources/zabbix/templates/template_app_service_ports.xml
[i] Importing actions..
    {'jsonrpc': '2.0', 'result': {'actionids': [7]}, 'id': 1}
[i] Getting IPs from maxmind database
[i] Importing hosts..
    192.168.0.179
    ...

```

## Options

If you want to import a new template, you can place it in "resources/zabbix/templates/".


## Troubleshooting

Zabbix Discover:

```bash
$ docker ps
$ docker logs -f zabbix | grep discover
```

Openvas NVT:

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

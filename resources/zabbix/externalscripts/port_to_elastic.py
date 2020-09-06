'''
        This script is executed on Zabbix Action, when the discovery found a new port,
        it send the host ip and the port and update the doc in elasticsearch.
                @alexfrancow

        https://stackoverflow.com/questions/46728783/how-to-update-tags-array-list-in-elasticsearch-and-python
        https://discuss.elastic.co/t/is-there-any-way-to-update-multiple-fields-by-update-by-query/70644/2
'''

from elasticsearch import Elasticsearch, helpers
import requests
import sys
import argparse

def add_ports(es, ip, port, port_w_protocol):
        # Add array and nested object ctx._source.ports_w_protocol.add(params.dict);
        doc = {
                "script" : {
                        "inline":"ctx._source.ports.add(params.dict)",
                        "params":{
                                "port" : port,
                                "dict" : {
                                        port : port_w_protocol
                                }
                        },
                        "lang"   : "painless"
                },
                "query" : {
                        "term": {
                                "ip" : ip
                        }
                }
        }
        res = es.update_by_query(index="isoc", body=doc)
        print(res)

def delete_ports(es, ip, port, port_w_protocol):
        doc = {
                "script" : {
                        "inline":"for(int i=0; i<ctx._source.ports.length; i++) {if(ctx._source.ports[i].containsKey(params.port)){ctx._source.ports.remove(i);}}",
                        "params":{
                                "port" : port
                        },
                        "lang":"painless"
                },
                "query" : {
                        "term": {
                                "ip" : ip
                        }
                }
        }
        res = es.update_by_query(index="isoc", body=doc)
        print(res)


parser = argparse.ArgumentParser(description='')
parser.add_argument('-i', '--ip', help='IP address to scan', type=str, action="store")
parser.add_argument('-pA', '--portAdd', help='Port to add in mongodb', type=str, action="store")
parser.add_argument('-pD', '--portDelete', help='Port to delete in mongodb', type=str, action="store")
args = parser.parse_args()


if args.ip and args.portAdd or args.portDelete:
        es = Elasticsearch([{'host':'192.168.1.129','port':9200}])
        INDEX_NAME = "isoc"

        if args.portAdd:
                # Zabbix problem example: 'Status of port 80 tcp http'
                portAdd = args.portAdd.split(" ")[3]
                portProtocol = args.portAdd.split(" ")[5]
                add_ports(es, args.ip, portAdd, portProtocol)

                # Get web info
                if "http" in portProtocol:
                        req = requests.get("http://"+x['ip']+":"+portAdd, verify=False)
                        collection.update({'ip': x['ip']}, {'$set': {'web_headers': req.headers}})
                        content = str(req.text.encode('utf-8'))
                        collection.update({'ip': x['ip']}, {'$set': {'web_payload': content}})

        else:
                portDelete = args.portDelete.split(" ")[3]
                portProtocol = args.portDelete.split(" ")[5]
                delete_ports(es, args.ip, portDelete, portProtocol)



"""queries to test in kibana
GET isoc/_search
{
 "query":
        { "term":
                { "ip": "2.136.66.201"
    }
  }
}

POST isoc/_update_by_query?conflicts=proceed
{
"script" : {
        "source":"for(int i=0; i<ctx._source.ports.length; i++) {if(ctx._source.ports[i].containsKey(params.port)){ctx._source.ports.remove(i);}}",
        "params":{
                "port" : "81"
        },
        "lang":"painless"
        },
"query" : {
        "term": {
                "ip" : "2.136.66.201"
                        }
                }
        }
"""

'''
        This script is executed on Zabbix Action, when the discovery found a new port,
        it send the host ip and the port and update the collection on mongodb.
                @alexfrancow

        https://stackoverflow.com/questions/33189258/append-item-to-mongodb-document-array-in-pymongo-without-re-insertion
        https://docs.mongodb.com/manual/reference/operator/update/pull/
'''

from pymongo import MongoClient
import requests
import sys
import argparse

def add_ports(coll, ip, port, port_w_protocol):
        coll.update({'ip': ip}, {'$push': {'ports': port}})
        coll.update({'ip': ip}, {'$set': {'ports_w_protocol.'+port: port_w_protocol}})

def delete_ports(coll, ip, port, port_w_protocol):
        coll.update({'ip': ip}, {'$pull': {'ports': port}})
        coll.update({'ip': ip}, {'$unset': {'ports_w_protocol.'+port: port_w_protocol}})



parser = argparse.ArgumentParser(description='')
parser.add_argument('-i', '--ip', help='IP address to scan', type=str, action="store")
parser.add_argument('-pA', '--portAdd', help='Port to add in mongodb', type=str, action="store")
parser.add_argument('-pD', '--portDelete', help='Port to delete in mongodb', type=str, action="store")
args = parser.parse_args()


if args.ip and args.portAdd or args.portDelete:
        client = MongoClient("192.168.1.129",
                username="alexfrancow",
                password="abc123",
                maxPoolSize=50)
        db = client.iSOC
        collection = db['assets']
        myquery = { "ip": args.ip }
        mydoc = collection.find(myquery)

        if args.portAdd:
                # Zabbix problem example: 'Status of port 80 tcp http'
                portAdd = args.portAdd.split(" ")[3]
                portProtocol = args.portAdd.split(" ")[5]
                for x in mydoc:
                        add_ports(collection, x['ip'], portAdd, portProtocol)

                # Get web info
                if portProtocol == "http":
                        req = requests.get("http://"+x['ip']+":"+portAdd, verify=False)
                        collection.update({'ip': x['ip']}, {'$set': {'web_headers': req.headers}})
                        content = str(req.text.encode('utf-8'))
                        collection.update({'ip': x['ip']}, {'$set': {'web_payload': content}})

        else:
                portDelete = args.portDelete.split(" ")[3]
                portProtocol = args.portDelete.split(" ")[5]
                for x in mydoc:
                        delete_ports(collection, x['ip'], portDelete, portProtocol)

                # Get web info
                if portProtocol == "http":
                        collection.update({'ip': x['ip']}, {'$set': {'web_headers': "Null"}})
                        collection.update({'ip': x['ip']}, {'$set': {'web_payload': "Null"}})

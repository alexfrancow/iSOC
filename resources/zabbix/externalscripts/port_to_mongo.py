'''
        This script is executed on Zabbix Action, when the discovery found a new port,
	it send the host ip and the port and update the collection on mongodb.
                @alexfrancow

	https://stackoverflow.com/questions/33189258/append-item-to-mongodb-document-array-in-pymongo-without-re-insertion
	https://docs.mongodb.com/manual/reference/operator/update/pull/
'''

from pymongo import MongoClient
import sys
import argparse

def add_ports(coll, ip, port):
	coll.update({'ip': ip}, {'$push': {'ports': port}})

def delete_ports(coll, ip, port):
	coll.update({'ip': ip}, {'$pull': {'ports': port}})


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
		portAdd = args.portAdd.split(" ")[3]
		for x in mydoc:
			add_ports(collection, x['ip'], portAdd)

	else:
		portDelete = args.portDelete.split(" ")[3]
		for x in mydoc:
			delete_ports(collection, x['ip'], portDelete)

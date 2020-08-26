from pymongo import MongoClient

'''
	This script has queries to check the mongodb.
		@alexfrancow
'''

if __name__ == '__main__':
	client = MongoClient("localhost",
		username="alexfrancow",
		password="abc123",
		maxPoolSize=50)
	db = client.iSOC
	collection = db['assets']
	cursor = collection.find({})

	# List all servers
	'''
	count = 0
	for document in cursor:
		count += 1
		print(document)
	print("Total servidores", count)
	'''

	# List 'El Castrillon' servers (by postal code)
	'''
	myquery = { "zip_code": "15009" }
	mydoc = collection.find(myquery)
	count = 0
	for x in mydoc:
		count += 1
		print(x)
	print("Total servidores", count)
	'''

	# List 'El Castrillon' servers (only IPs)
        myquery = { "zip_code": "15009" }
	mydoc = collection.find(myquery)
	count = 0
	for x in mydoc:
		count += 1
		print(x['ip'])
	print("Total servidores", count)

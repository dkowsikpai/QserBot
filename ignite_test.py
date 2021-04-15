from pyignite import Client
import json

client = Client()
client.connect('127.0.0.1', 10800)

#Create cache
my_cache = client.get_or_create_cache('my cache')


data = json.dumps({'new_service': False, 'complaint': 'gorilla fan', 'desc': 'Not spinning', 'addr': '', 'mob': '', 'loc': '', 'lat': '', 'long': '', 'landmark': '', 'confirm': ''})
#Put value in cache
my_cache.put(1, data)

#Get value from cache
result = json.loads(my_cache.get(1))
print(result["complaint"])
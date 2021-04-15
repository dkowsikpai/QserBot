from pyignite import Client
import json

from config import *

class IgniteData:

    def __init__(self):
        client = Client()
        client.connect(ip, port)

        #Create cache
        self.my_cache = client.get_or_create_cache(cache)


    def putData(self, dt, idk):
        data = json.dumps(dt)
        #Put value in cache
        self.my_cache.put(idk, data)

    def getData(self, idk):
        #Get value from cache
        result = json.loads(self.my_cache.get(idk))
        return result

    def removeData(self, idk):
        self.my_cache.remove_key(idk)

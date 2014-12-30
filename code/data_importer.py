import sys, getopt
from pymongo import MongoClient, ReadPreference

class MongosConnection:
    
    def __init__(self, setup):
        stp = self.setup 
        
    def connectTo(self):    
        if stp == 's1'
            #connection for standalone setup          
            connection = MongoClient('127.0.0.1', 27017)
        elif stp == 's2'
            #uri for sharded mongos
            uri = "achaora-mongodb-1:27019,achaora-mongodb-2:27019,achaora-mongodb-3:27019"
            
            #connection for sharded mongos set-up
            connection = MongoClient(uri,
                           configdb=True,
                           config='/srv/mongodb/mongos.conf')
    return connection
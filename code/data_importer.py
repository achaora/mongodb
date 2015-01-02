import sys, getopt
from pymongo import MongoClient, ReadPreference

class MongosConnection:
    
    def __init__(self, setup):
        stp = self.setup 
        
    def connectTo(self):    
        if stp == 's1':
            #connection for standalone setup          
            connection = MongoClient('127.0.0.1', 27017)
        elif stp == 's2':
            #uri for sharded mongos
            uri = "achaora-mongodb-1:27019,achaora-mongodb-2:27019,achaora-mongodb-3:27019"
            
            #connection for sharded mongos set-up
            connection = MongoClient(uri,
                           configdb=True,
                           config='/srv/mongodb/mongos.conf')
        return connection
    
def importer(chunk):
    imp = 'mongoimport --db medicareSuppliers --collection supplier --ignoreBlanks --type tsv --headerline --file /data/rawdata/chunk'+str(chunk)+'.txt '
    return imp
    
def main(argv):
    setup = ''
    chunk = ''
    try:
        opts, args = getopt.getopt(argv,"hi:s:",["ifile=","setup="])
    except getopt.GetoptError:
        print 'data_importer.py -i <inputfile> -s [setup] \n'
        print '-i   data chunk to be imported \n'
        print 'SETUP \n'
        print 's1   standalone MongoDB server \n'
        print 's2   sharded MongoDB server cluster \n'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'data_importer.py -i <inputfile> -s [setup] \n'
            print '-i   data chunk to be imported \n'
            print 'SETUP \n'
            print 's1   standalone MongoDB server \n'
            print 's2   sharded MongoDB server cluster \n'
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup = arg
        elif opt in ("-i", "--ifile"):
            chunk = arg    
    return setup, chunk
   
if __name__ == '__main__':
    main(sys.argv[1:])
    connect = MongosConnection(setup)
    instance = connect.connectTo()
    db = instance.medicareProviders
    
import sys, getopt
from pymongo import MongoClient, ReadPreference

class MongosConnection:
    
    def __init__(self, setup):
        self.stp = setup 
        self.connect = MongoClient()
        
    def mongosInstance(self):    
        if self.stp == 'standalone':
            #connection for standalone setup          
            self.connect = MongoClient('127.0.0.1', 27017)
        elif self.stp == 'sharded':
            #uri for sharded mongos
            uri = "achaora-mongodb-1:27019,achaora-mongodb-2:27019,achaora-mongodb-3:27019"
            
            #connection for sharded mongos set-up
            self.connect = MongoClient(uri)
        
        return self.connect
    
def importer(chunk):
    ingest = 'mongoimport --db medicareSuppliers --collection supplier --ignoreBlanks --type tsv --headerline --file /data/rawdata/'+str(chunk)
    return ingest
    
def main(argv):
    setup = ''
    chunk = ''
    try:
        opts, args = getopt.getopt(argv,"hi:s:",["ifile=","setup="])
    except getopt.GetoptError:
        print '\nUsage: data_importer.py -i <inputfile> -s [setup] \n'
        print '<inputfile>  -data chunk to be imported \n'
        print 'SETUP \n'
        print 'standalone  -standalone MongoDB server \n'
        print 'sharded  -sharded MongoDB server cluster \n'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '\nUsage: data_importer.py -i <inputfile> -s [setup] \n'
            print '<inputfile>  -data chunk to be imported \n'
            print 'SETUP \n'
            print 'standalone  -standalone MongoDB server \n'
            print 'sharded  -sharded MongoDB server cluster \n'
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup = arg
        elif opt in ("-i", "--ifile"):
            chunk = arg    
    return setup, chunk
   
if __name__ == '__main__':
    args = {} 
    args = main(sys.argv[1:])
    setup = args[0]
    #print setup
    chunk = args[1]
    #print chunk
    selected = MongosConnection(setup)
    instance = selected.mongosInstance()
    db = instance.medicareSuppliers
    importer(chunk)
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
    
def main(argv):
    inputfile = ''
    try:
        opts, args = getopt.getopt(argv,"h","s1","s2")
    except getopt.GetoptError:
        print 'data_importer.py -[options] -i <inputfile>'
        print 'OPTIONS'
        print '-s1   connection for standalone MongoDB server'
        print '-s2   connection for sharded MongoDB server cluster'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'performance_tester.py -[options]'
            print 'OPTIONS'
            print '-s1   connection for standalone MongoDB server'
            print '-s2   connection for sharded MongoDB server cluster'
            sys.exit()
        elif opt in ("-s1", "--setup1"):
            inputfile = arg
        elif opt in ("-s2", "--setup2"):
            inputfile = arg
    return inputfile
   
if __name__ == '__main__':
    main(sys.argv[1:])
    inputfile = main(sys.argv[1:])
    datafile = open(inputfile)
    number_of_chunks = 10
    chunk = {}
    for chunk_number in range(number_of_chunks):
        print 'Processing chunk'+str(chunk_number)+'.txt... \n'
        chunk[chunk_number] = DataChunker(datafile, chunk_number, number_of_chunks)
        chunk[chunk_number].work()
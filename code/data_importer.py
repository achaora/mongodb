import sys, getopt
from subprocess import call
from pymongo import MongoClient, ReadPreference

class MongosConnection:

    def __init__(self, setup):
        self.stp = setup
        self.connect = MongoClient()

    def mongosInstance(self):
        if self.stp == 'standalone':

            #uri for standalone mongos
            uri = "mongodb://siteRootAdmin:zarura@achaora-005:27017"

            #connection for standalone setup
            self.connect = MongoClient(uri)
        elif self.stp == 'sharded':
            #uri for sharded mongos
            uri = "mongodb://siteRootAdmin:zarura@achaora-001:27022"

            #connection for sharded mongos set-up
            self.connect = MongoClient(uri)

        return self.connect

def importer(chunk):
    if chunk == 'chunk1.txt':
        ingest = 'mongoimport --host achaora-005 --port 27017 --username siteRootAdmin --password zarura --db medicareSuppliers --collection supplier --ignoreBlanks --type tsv --headerline --file ~/data/'+str(chunk)
    else:
        ingest = 'mongoimport --host achaora-005 --port 27017 --username siteRootAdmin --password zarura --db medicareSuppliers --collection supplier --ignoreBlanks --type tsv --file ~/data/'+str(chunk)
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
    #supplier = db.supplier
    print str(db)
    call(importer(chunk))
    print str(chunk)+" successfully imported"

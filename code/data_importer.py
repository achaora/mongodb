import sys, getopt
import shlex, subprocess
from pymongo import MongoClient, ReadPreference

class MongosConnection:

    def __init__(self, setup):
        self.stp = setup
        self.connect = MongoClient()

    def mongosInstance(self):
        if self.stp == 'standalone':

            #uri for standalone mongod
            uri = "mongodb://siteRootAdmin:zarura@achaora-006:27017"

            #connection for standalone setup
            self.connect = MongoClient(uri)
        elif self.stp == 'sharded':
            #uri for sharded mongos
            uri = "mongodb://siteRootAdmin:zarura@achaora-001:27022"

            #connection for sharded mongos set-up
            self.connect = MongoClient(uri)

        return self.connect


class ServerShell:

     def __init__(self, setup):
         self.stp = setup

     def serverInstance(self):
         if self.stp == 'standalone':
            #connection for standalone mongo
            host = 'achaora-006'
            port = '27017'
            username = 'siteRootAdmin'
            password = 'zarura'

         elif self.stp == 'sharded':
            #connection for sharded mongo
            host = 'achaora-001'
            port = '27022'
            username = 'siteRootAdmin'
            password = 'zarura'

         return host, port, username, password

def importer(chunk, setup, host, port, username, password):
    if setup == 'standalone':
        if chunk == 'chunk1.txt':
            ingest = 'mongoimport --host '+host+' --port '+port+' --username '+username+' --password '+password+' --authenticationDatabase admin --db medicareSuppliers --collection supplier --
ignoreBlanks --type tsv --headerline --file '+str(chunk)
        else:
            ingest = 'mongoimport --host '+host+' --port '+port+' --username '+username+' --password '+password+' --authenticationDatabase admin --db medicareSuppliers --collection supplier --
ignoreBlanks --type tsv --headerline --file '+str(chunk)
    elif setup == 'sharded':
        if chunk == 'chunk1.txt':
            ingest = 'mongoimport --host '+host+' --port '+port+' --username '+username+' --password '+password+' --authenticationDatabase admin --db medicareSuppliers --collection supplier --ignoreBlanks --type tsv --headerline --file '+str(chunk)
        else:
            ingest = 'mongoimport --host '+host+' --port '+port+' --username '+username+' --password '+password+' --authenticationDatabase admin --db medicareSuppliers --collection supplier --ignoreBlanks --type tsv --headerline --file '+str(chunk)

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
    parameters = {}
    connection = MongosConnection(setup)
    selected = ServerShell(setup)
    connected = connection.mongosInstance()
    instance = selected.serverInstance()
    parameters = instance
    print parameters[0]
    db = connected.medicareSuppliers
    supplier = db.supplier
    #print str(db)
    cmdMongoImport = importer(chunk,setup,parameters[0],parameters[1],parameters[2],parameters[3])
    subpMongoImport = shlex.split(cmdMongoImport)
    print 'Data importing from'+str(chunk)+' ...\n'
    subprocess.Popen(subpMongoImport)


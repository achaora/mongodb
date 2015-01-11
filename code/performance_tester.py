import sys, getopt
from pymongo import MongoClient, ReadPreference

class MongosConnection:
    
    def __init__(self, setup):
        self.stp = setup 
        self.connect = MongoClient()
        
    def mongosInstance(self):    
        if self.stp == 'standalone':
            #connection for standalone setup          
            self.connect = MongoClient('localhost', 27017)
        elif self.stp == 'sharded':
            #uri for sharded mongos
            uri = "achaora-mongo-001"
            
            #connection for sharded mongos set-up
            self.connect = MongoClient(uri, 27022)
        
        return self.connect

        
class AggregateQuery:
    
    def __init__(self):
        self.query = ''
        
    def stateAvgs(self):
        self.query = ("db.supplier.aggregate("
	"   ["
	"    {"
	"     $group:" 
	"        {"
	"	    _id:'$nppes_provider_state'," 
	"	    avg_claim: {$avg: '$average_submitted_chrg_amt'},"
	"	    avg_payment: {$avg: '$average_Medicare_payment_amt'}"
	"        }"
	"    }"
	"   ]"
        " )")         
        return self.query

        
class MapReduceQuery:
    
    def __init__(self):
        self.mapcode = ''
        self.reducecode = ''
        self.finalizecode = ''
        self.query = ''

    def mapFunction(self): 
        self.mapcode = ("var mapFunction = function() {"
        "var key = this.nppes_provider_state;"
	"var value = {"
	"		count: 1,"
	"		claim: this.average_submitted_chrg_amt,"
	"		payment: this.average_Medicare_payment_amt"
	"	     };"
        "emit(key, value);"
        "};")
        return self.mapcode

    def reduceFunction(self):
        self.reducecode = ("var reduceFunction = function(keyState, countStVals) {"
	"reduceVal = {count: 0, claim: 0, payment: 0};"	
	"for (var provider = 0; provider < countStVals.length; provider++) {"
	"		reduceVal.count += countStVals[provider].count;" 
	"		reduceVal.claim += countStVals[provider].claim;"
	"		reduceVal.payment += countStVals[provider].payment;"
	"		};"
        "  return reduceVal;"
        "};")            
        return self.reducecode
    
    def finalizeFunction(self):
        self.finalizecode = ("var finalizeFunction = function(keyState, reduceVal) {"
	"reduceVal.avg = {"
	"  avg_claim: reduceVal.claim/reduceVal.count,"
     	"  avg_payment: reduceVal.payment/reduceVal.count"
	"};"	
		
	"return reduceVal;"
        "};")            
        return self.finalizecode

    def stateAvgs(self):
        self.query = ""+str(self.mapFunction()) +"\n"+str(self.reduceFunction())+"\n"+str(self.finalizeFunction())+"\n"
        self.query += "db.supplier.mapReduce( mapFunction,"
        self.query += " reduceFunction,"
        self.query += " {"
        self.query += "  out: { merge: 'map_reduce_suppliers_states' },"
        self.query += "  finalize: finalizeFunction"
        self.query += "  }"
        self.query += " )"
        return self.query
    
def main(argv):
    setup = ''
    query = ''
    try:
        opts, args = getopt.getopt(argv,"hs:q:",["setup=","query"])
    except getopt.GetoptError:
        print '\nUsage: performance_tester.py -s [setup] -q [query] \n'
        print 'SETUP \n'
        print 'standalone  -connection for standalone MongoDB server \n'
        print 'sharded  -connection for sharded MongoDB server cluster \n'
        print 'QUERY \n'
        print 'aggregate  -aggregate query \n'
        print 'mapreduce  -mapreduce query \n'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '\nUsage: performance_tester.py -s [setup] -q [query] \n'
            print 'SETUP \n'
            print 'standalone  -connection for standalone MongoDB server \n'
            print 'sharded  -connection for sharded MongoDB server cluster \n'
            print 'QUERY \n'
            print 'aggregate  -aggregate query \n'
            print 'mapreduce  -mapreduce query \n'
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup = arg
        elif opt in ("-q", "--query"):
            query = arg
    return setup, query
   
if __name__ == '__main__':
    args = {}
    args = main(sys.argv[1:])
    setup = args[0]
    #print setup 
    query = args[1]
    #print query
    selected = MongosConnection(setup)
    instance = selected.mongosInstance()
    db = instance.medicareSuppliers
    print "Connected to shard: "+str(db.connection.is_mongos)
    print "Primary db server connection: "+str(db.connection.host)
    if query == 'aggregate':
        run = AggregateQuery()
        print str(run)
        for test in range(3):
            print 'Aggregate query on '+setup+': performance test...pass '+str(test + 1)+' of 3. \n'
            run.stateAvgs()
            print str(run.stateAvgs())
    elif query == 'mapreduce':
        run = MapReduceQuery()
        print str(run)
        for test in range(3):
            print 'Mapreduce query on '+setup+ ': performance test...pass '+str(test + 1)+' of 3. \n'
            run.stateAvgs()
            print str(run.stateAvgs())
    db.connectcion.close() 
 
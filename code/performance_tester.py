import sys, getopt
from mongoengine import *
from mongoengine.context_managers import switch_db
from .data_importer.py import MongosConnection

class AggregateQuery:
    
    def __init__(self):
        
    def stateAvgs(self):
        query = "db.supplier.aggregate("
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
            " )"         
    return query

        
class MapReduceQuery:
    
    def __init__(self):

    def mapFunction(self): 
        code = "function() {"
            "var key = this.nppes_provider_state;"
	    "var value = {"
	    "		count: 1,"
	    "		claim: this.average_submitted_chrg_amt,"
	    "		payment: this.average_Medicare_payment_amt"
	    "	     };"
            "emit(key, value);"
            "};"
    return code

    def reduceFunction(self):
        code = "function(keyState, countStVals) {"
	    "reduceVal = {count: 0, claim: 0, payment: 0};"	
	    "for (var provider = 0; provider < countStVals.length; provider++) {"
	    "		reduceVal.count += countStVals[provider].count;" 
	    "		reduceVal.claim += countStVals[provider].claim;"
	    "		reduceVal.payment += countStVals[provider].payment;"
	    "		};"
            "  return reduceVal;"
            "};"            
    return code
    
    def finalizeFunction(self):
        code = "function(keyState, reduceVal) {"
	    "reduceVal.avg = {"
	    "  avg_claim: reduceVal.claim/reduceVal.count,"
     	    "  avg_payment: reduceVal.payment/reduceVal.count"
	    "};"	
		
	    "return reduceVal;"
            "};"            
    return code

    def stateAvgs(self):
        query = "db.supplier.mapReduce("+ self.mapFunction()+","
            " "+self.reduceFunction()+","
            " {"
            "  out: { merge: 'map_reduce_suppliers_states' },"
            "  finalize:"+self.finalizeFunction()+" "
            "  }"
            " )"
    return query
    
def main(argv):
    setup = ''
    query = ''
    try:
        opts, args = getopt.getopt(argv,"hs:q:",["setup=","query"])
    except getopt.GetoptError:
        print 'performance_tester.py -s [setup] -q [query] \n'
        print 'SETUP \n'
        print 's1   connection for standalone MongoDB server \n'
        print 's2   connection for sharded MongoDB server cluster \n'
        print 'QUERY \n'
        print 'q1   aggregate query \n'
        print 'q2   mapreduce query \n'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'performance_tester.py -s [setup] -q [query] \n'
            print 'SETUP \n'
            print 's1   connection for standalone MongoDB server \n'
            print 's2   connection for sharded MongoDB server cluster \n'
            print 'QUERY \n'
            print 'q1   aggregate query \n'
            print 'q2   mapreduce query \n'
            sys.exit()
        elif opt in ("-s", "--setup"):
            setup = arg
        elif opt in ("-q", "--query"):
            query = arg
    return setup, query
   
if __name__ == '__main__':
    main(sys.argv[1:])
    connect = MongosConnection(setup)
    connect.connectTo()
    if query == 'q1':
        run = AggregateQuery()
    elif query == 'q2':
        run = MapReduceQuery()
    for test in range(3):
        print 'Performance test...pass '+str(test + 1)+' of 3. \n'
        run.stateAvgs()
    


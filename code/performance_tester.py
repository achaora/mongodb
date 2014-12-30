import sys, getopt
from mongoengine import *
from mongoengine.context_managers import switch_db
from .data_importer.py import MongosConnection

class AggregateQuery:
    
    def __init__(self, chunk_number):
        self.chn = chunk_number
        
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
    
    def __init__(self, chunk_number):

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
    try:
        opts, args = getopt.getopt(argv,"h","s1","s2")
    except getopt.GetoptError:
        print 'performance_tester.py -[options]'
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
    


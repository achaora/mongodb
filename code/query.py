from mongoengine import *
from mongoengine.context_managers import switch_db
from pymongo import MongoClient, ReadPreference

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

    def mapReduceFunction(self):
        query = "db.supplier.mapReduce("+ self.mapFunction()+","
            " "+self.reduceFunction()+","
            " {"
            "  out: { merge: 'map_reduce_suppliers_states' },"
            "  finalize:"+self.finalizeFunction()+" "
            "  }"
            " )"
    return query
    
#uri for sharded mongos
uri = "achaora-mongodb-1:27019,achaora-mongodb-2:27019,achaora-mongodb-3:27019"

#connection for sharded mongos set-up
setuptwo = MongoClient(uri,
                       configdb=True,
                       config='/srv/mongodb/mongos.conf')

#connection for standalone setup          
setupone = MongoClient('127.0.0.1', 27017)


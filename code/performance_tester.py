import sys, getopt
import array
import datetime
from pymongo import MongoClient, ReadPreference
from bson.son import SON
from bson.code import Code
from datetime import timedelta

class MongosConnection:

    def __init__(self, setup):
        self.stp = setup
        self.connect = MongoClient()

    def mongosInstance(self):
        if self.stp == 'standalone':
            #mongoDB URI for standalone mongod
            uri = "mongodb://siteRootAdmin:zarura@achaora-005:27017"
            #connection for standalone setup
            self.connect = MongoClient(uri)
        elif self.stp == 'sharded':
            #mongoDB URI for sharded mongos
            uri = "mongodb://siteRootAdmin:zarura@achaora-001:27022"

            #connection for sharded mongos set-up
            self.connect = MongoClient(uri)

        return self.connect


class AggregateQuery:

    def __init__(self):
        self.query = ''

    def stateAvgs(self):
        self.query = [
          {
             "$group":
                {
                    "_id":"$nppes_provider_state",
                    "avg_claim": {"$avg": "$average_submitted_chrg_amt"},
                    "avg_payment": {"$avg": "$average_Medicare_payment_amt"}
                }
            }
           ]
        return self.query


class MapReduceQuery:

    def __init__(self):
        self.mapcode = ''
        self.reducecode = ''
        self.finalizecode = ''
        self.query = ''

    def mapFunction(self):
        self.mapcode = Code("function() {"
                            "  var key = this.nppes_provider_state;"
                            "  var value = {"
                            "  count: 1,"
                            "  claim: this.average_submitted_chrg_amt,"
                            "  payment: this.average_Medicare_payment_amt"
                            " };"
                            " emit(key, value);"
                            "};")
        return self.mapcode

    def reduceFunction(self):
        self.reducecode = Code("function(keyState, countStVals) {"
                                "  reduceVal = {count: 0, claim: 0, payment: 0};"
                                "  for (var provider = 0; provider < countStVals.length; provider++) {"
                                "    reduceVal.count += countStVals[provider].count;"
                                "    reduceVal.claim += countStVals[provider].claim;"
                                "    reduceVal.payment += countStVals[provider].payment;"
                                "  };"
                                "  return reduceVal;"
                                "};")
        return self.reducecode

    def finalizeFunction(self):
        self.finalizecode = Code("function(keyState, reduceVal) {"
                                 "  reduceVal.avg = {"
                                 "  avg_claim: reduceVal.claim/reduceVal.count,"
                                 "  avg_payment: reduceVal.payment/reduceVal.count"
                                 "};"
                                 "return reduceVal;"
                                 "};")
        return self.finalizecode


    def outputCollection(self):
        self.query = "{ merge: 'map_reduce_suppliers_states'}"
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
    supplier = db.supplier
    performance = db.performance_metric
    tstart = {}
    tend = {}
    tdifference = {}
    timeTotal = {}
    #print "Connected to shard: "+str(db.connection.is_mongos)
    print "Connected to shard: "+str(supplier)
    print "Primary db server connection: "+str(db)

    if query == 'aggregate':
        run = AggregateQuery().stateAvgs()
        print str(run)
        for test in range(3):
	    print '\nPerformance Test \t:Pass '+str(test + 1)+' of 3.'
	    print 'Mongodb Environment\t:'+setup
            print 'Query Type\t\t:Aggregate Query \nExecuting benchmark query...'
            tstart[test] = datetime.datetime.now()
            supplier.aggregate(run)
            tend[test] =  datetime.datetime.now()
            print 'Time Started\t\t:'+str(tstart[test])
            print 'Time Ended\t\t:'+str(tend[test])
            tdifference[test] = tend[test] - tstart[test]
            print 'Duration of Pass '+str([test + 1])+'\t:'+str(tdifference[test])
            print 'Display Query Results:\n'
	    print list((supplier.aggregate(run)))
            #print str(db.supplier.find_one())
            #print 'Pass '+str(test + 1)+' query execution time = '+str(tdifference[test])
            #timeTotal[test]+= tdifference[test]
    elif query == 'mapreduce':
        run = MapReduceQuery()
        print str(run)
        mapStep = run.mapFunction()
        reduceStep = run.reduceFunction()
        finalizeStep = run.finalizeFunction()
        outStep = run.outputCollection()
        for test in range(3):
            print '\nPerformance Test \t:Pass '+str(test + 1)+' of 3.'
            print 'Mongodb Environment\t:'+setup
            print 'Query Type\t\t:Mapreduce Query \nExecuting benchmark query...'
            tstart[test] = datetime.datetime.now()
            supplier.map_reduce(mapStep,reduceStep,outStep,finalize = finalizeStep)
            tend[test] =  datetime.datetime.now()
            print 'Time Started\t\t:'+str(tstart[test])
            print 'Time Ended\t\t:'+str(tend[test])
            tdifference[test] = tend[test] - tstart[test]
            print 'Duration of Pass '+str([test + 1])+'\t:'+str(tdifference[test])
            print 'Display Query Results:\n'
            result = supplier.map_reduce(mapStep,reduceStep,outStep,finalize = finalizeStep)

            for doc in result.find():
                print doc
    
    timeTotal = tdifference[0] + tdifference[1] + tdifference[2]
    durationAv = str(timeTotal/3)
    print '\nThe average execution time for this '+query+' query on the '+setup+' mongodb server environment for the 3 iterations was:'+durationAv
    recNo = supplier.count()
    print 'The number of documents the query ran on was\t:'+str(recNo)
    saveMetric = performance.insert_one({ 'environment': setup , 'query_type': query , 'avg_time': durationAv, 'no_of_docs': recNo }) 
    resultsFile = open("metrics.csv", 'a')
    newInput = setup+'-'+query+','+str(recNo)+','+durationAv+'\n'
    #print newInput
    resultsFile.write(newInput)
    print "These metrics have been saved in the 'performance_metric' collection of the queried database\n" 

    #db.connection.close()

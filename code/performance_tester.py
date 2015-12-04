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
    tstart = {}
    tend = {}
    tdifference = {}
    timeTotal = tdifference
    #print "Connected to shard: "+str(db.connection.is_mongos)
    print "Connected to shard: "+str(supplier)
    print "Primary db server connection: "+str(db)

    if query == 'aggregate':
        run = AggregateQuery().stateAvgs()
        print str(run)
        for test in range(3):
            print 'Aggregate query on '+setup+': performance test...pass '+str(test + 1)+' of 3. \n'
            tstart[test] = datetime.datetime.now()
            print str(tstart[test])
            supplier.aggregate(run)
            tend[test] =  datetime.datetime.now()
            print str(tend[test])
            tdifference[test] = tend[test] - tstart[test]
            print str(tdifference[test])
            print (list(supplier.aggregate(run)))
            #print str(db.supplier.find_one())
            print 'Pass '+str(test + 1)+' query execution time = '+str(tdifference[test])
            timeTotal[test]+= tdifference[test]
    elif query == 'mapreduce':
        run = MapReduceQuery()
        print str(run)
        mapStep = run.mapFunction()
        reduceStep = run.reduceFunction()
        finalizeStep = run.finalizeFunction()
        outStep = run.outputCollection()
        for test in range(3):
            #print 'Mapreduce query on '+setup+ ': performance test...pass '+str(test + 1)+' of 3. \n'
            #print supplier.map_reduce(mapStep,reduceStep,outStep,finalize = finalizeStep)a
            tstart[test] = datetime.datetime.now()
            print str(tstart[test])
            supplier.map_reduce(mapStep,reduceStep,outStep,finalize = finalizeStep)
            tend[test] =  datetime.datetime.now()
            print str(tend[test])
            tdifference[test] = tend[test] - tstart[test]
            print str(tdifference[test])
            result = supplier.map_reduce(mapStep,reduceStep,outStep,finalize = finalizeStep)

            for doc in result.find():
                print doc

            print 'Pass '+str(test + 1)+' query execution time = '+str(tdifference[test])
            timeTotal[test]+= tdifference[test]

    print 'The average execution time for this '+query+' query on the '+setup+' mnongodb server environment is '+str(timeTotal[test]/3)+' for the 3 iterations'

    #db.connection.close()

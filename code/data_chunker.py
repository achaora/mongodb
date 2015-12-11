#Takes in a data file and breaks it down into chunks for
#performance anaylsis based on data-set size
import sys, getopt

class DataChunker:

    def __init__(self, datafile, chunk_number, number_of_chunks):
        self.dat = datafile
        self.chn = chunk_number
        self.nch = number_of_chunks


    def getFileSize(self): #get size of file
        self.dat.seek(0,2)
        return self.dat.tell()

    def work(self):
        #cursors for start and end on current chunk
        start = self.getFileSize() * self.chn / self.nch
        end = self.getFileSize() * (self.chn + 1) / self.nch
        fname = 'chunk'+str(self.chn + 1)+'.txt'
        wf = open(fname,'a')

        if start <= 0:
            self.dat.seek(0,0)
        else:
            self.dat.seek(start,0)

        #iterate to end of chunk reading file content and writing to chunk file
        while self.dat.tell() < end:
            content = self.dat.readline()
            wf.write(content)

        return
            
def main(argv):
   inputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
   except getopt.GetoptError:
      print 'data_chunker.py -i <inputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'data_chunker.py -i <inputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
   return inputfile

if __name__ == '__main__':
    main(sys.argv[1:])
    inputfile = main(sys.argv[1:])
    datafile = open(inputfile)
    number_of_chunks = 10
    chunk = {}
    for chunk_number in range(number_of_chunks):
        print 'Processing chunk'+str(chunk_number + 1) +'.txt... \n'
        chunk[chunk_number] = DataChunker(datafile, chunk_number, number_of_chunks)
        chunk[chunk_number].work()

#INSTRUCTIONS:

I. 	Set up server environments<br>
II.	Download and chunk data-set<br> 
III 	Import data chunk into databases<br>
IV.	Execute performance scripts<br>
V	Repeat III and IV to increment data-set sizes and execute performance scripts<br>
VI.	Vizualize performance results<br>


###I. SET UP SERVER ENVIRONMENTS	

####Set Up 1: Mongos VM Connecting to Standalone Mongod VM

_Setting up Mongos (database router) VM:_

1. Spin up an Openstack VM and install Cloudmesh using the instructions found here: [Quickstart for an Openstack VM](http://cloudmesh.github.io/introduction_to_cloud_computing/cloudmesh/setup/setup_openstack.html). The Openstack VM running Cloudmesh will serve as a MongoDB router. 
 
    If unable to successfully install Cloudmesh on the Openstack VM, spin up a second Openstack VM for the Standalone Mongod and skip     steps 1 and 2 in the sub-section below (Setting up Standalone Mongod VM). Then [follow these     instructions](https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/) to install MongoDB on the Standalone Mongod VM.

    *make sure to share ssh keys between the VMs (i.e. for each server in the set up, add the public keys of the other servers to the 'authorized_keys' file). To facilitate host discovery also consider adding each server and its IP(s) to the /etc/hosts file of each VM.

_Setting up Standalone Mongod (database) VM:_

1. Run script vm_standalone_builder.py to create a VM for housing the stand-alone MongoDB database

2. Install the latest stable version of MongoDB on the VM created by issuing the commands:
	
		$ sudo apt-get update
		$ sudo apt-get install -y mongodb-org

3. Ensure that the permissions on folders /var/log/mongodb and /var/lib/mongodb are restricted but set to where they can be read by the account (user 'ubuntu') under which the MongoDB services will run. By default these will be set for use by user 'mongodb'.

4. Start the MongoDB server by issuing the command below:

		$ mongod --config /etc/mongod.conf
	
5. From the shell of the Standalone Mongod VM connect to the standalone database and create the appropriate user accounts by issuing the command:

		$ mongo
   and running the commands in the provided set up file [database_accounts.txt](./setup/database_accounts.txt)  

6. Test connection to Standalone Mongod from MongoDB router VM by running the command below and verifying if connection is established:

		$mongo --host $USER-00X --port 27017
		
			(where $USER-00X is the name of the Standalone Mongod VM) 

####Set Up 2: Mongos VM Connecting to Sharded 3 VM Cluster

_Setting up Mongos (database router) VM:_

1. Install Cloudmesh on VM using the instructions found here:  [Quickstart for an Openstack VM](http://cloudmesh.github.io/introduction_to_cloud_computing/cloudmesh/setup/setup_openstack.html) . The server running Cloudmesh will serve as the mongos. Alternatively, reuse the router server in 'Set Up 1' above.

    If unable to successfully install Cloudmesh on the Openstack VM, spin up 3 new Openstack VMs for the Sharded Cluster and skip     steps 1 and 2 in the sub-section below (Setting up Sharded Cluster). Then [follow these instructions to install MongoDB on each of the     3 Ubuntu VMs](https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/).
    
    *make sure to share ssh keys between the VMs (i.e. for each server in the set up, add the public keys of the other servers to the 'authorized_keys' file). To facilitate host discovery also consider adding each server and its IP(s) to the /etc/hosts file of each VM.

_Setting up Sharded (distributed database) Cluster:_

1. From the mongos, run the script vm_cluster_builder.py to create a 3 node cluster for hosting the sharded MongoDB. 

2. Install the latest stable version of MongoDB on the VMs created by issuing the commands:
	
		$ sudo apt-get update
		$ sudo apt-get install -y mongodb-org

3. Generate a keyFile for use with server authentication within the cluster by running the openssl command: 

		$ openssl rand -base64 741 > mongodb-keyfile

   The above will ensure that the keyFile created is long and random, and only contains characters in base64 set, as is required by MongoDB for key files. 

4. Restrict permissions on the keyFile to the MongoDB owner by issuing the command:

		$ chmod 600 mongodb-keyfile 

5. Copy the file keyfile, mongodb-keyfile, to all servers in the set-up, including the mongos server. Create and place the keyfile in an obscure directory/path with permissions set to where it is readable by the MongoDB owner.

6. Update the provided sample yaml files [mongos.conf](./config/mongos.conf), [configsvr.conf](./config/configsvr.conf) and [shardsvr.conf](./config/shardsvr.conf) files with the correct path to the mongodb-keyfile on each server (find lines with place-holding text for the keyfile path).

7. Create data directories on each of the three cluster servers and ensure that the account running MongoDB has read and write access to them.

		$ mkdir /data/configdb

8. Place the [mongos.conf](./config/mongos.conf) file in the /etc folder of the mongos server. 

9. Place the [configsvr.conf](./config/configsvr.conf) and [shardsvr.conf](./config/shardsvr.conf) files in an appropriate folder e.g. /svr/mongodb  on each of the 3 servers. Under this configuration, each of the servers in the 3 VM cluster will run the ‘configsvr’ and 'shardsvr' roles. Note from the sample yaml files that these roles have to run on different ports, and the data for the two services have be located at different paths in order to run on the same VM. 
 
10. Place the shardsvr.conf file in the /svr/mongodb folder of each of the servers with the shard/database role. Ensure that the permissions on each of the conf files are restricted but set to where they can be read by the account (user 'ubuntu')  under which the MongoDB services run. By default these will be set for use by user 'mongodb.

11. Start the 'shardsvr' server services on each of the 3 VMs:

		$ mongod --config /svr/mongodb/shardsvr.conf --shardsvr

12. Start the 'configsvr' server services on the 3 VMs:
 
		 mongod --config /svr/mongodb/configsvr.conf --configsvr 

13. From the shell of each of the VMs running the 'shardsvr' service connect to the local MongoDB and create the appropriate user accounts by issuing the command:

		$ mongo
   and running the commands in the provided set up file [database_accounts.txt](./setup/database_accounts.txt)

14. Authenticate to the user with the database 'root' role from the mongo shell of each of the 'shardsvr' VMs to add shards to each of them:

		>db.auth("siteRootAdmin","zarura")
		
			*** a successful authentication will display >1 ***
		
		>sh.addShard( "$USER-00X:272018" )
		
			(where $USER-00X is the name of the VM)

15. Run the mongos server service on the router VM:

		$mongos --configdb $USER-00X1:27019,$USER-00X2:27019,$USER-00X3:27019 --config /svr/mongodb/mongos.conf
		
		(where $USER-00X1 - 3 are the names of the 'configsvr' cluster VMs)

16. Test connection to Sharded Cluster from MongoDB router VM by running the command below and verifying if connection is established:

		$mongo --host $USER-00X --port 27022
		
			(where $USER-00X is the name of the MongoDB router VM)


###II. DOWNLOAD AND CHUNK DATA-SET

1. Download the tab delimited ['Medicare Provider Data - Physicians and Other Suppliers'](http://www.cms.gov/apps/ama/license-2011.asp?file=http://download.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Medicare-Provider-Charge-Data/Downloads/Medicare-Physician-and-Other-Supplier-PUF-CY2012.zip) dataset archive file from Data.gov.

(N.B. The data set used in this evaluation appears to no longer be available through the link on Data.gov. For access to an archived copy on IU Box, please contact the author. Instructors of B590 would have received an invitation to the Box folder with the data)  

2. Extract the dataset file from the archive and move it into the cloned ./data folder

		$unzip .../Medicare-Physician-and-Other-Supplier-PUF-CY2012.zip
		$mv .../Medicare-Physician-and-Other-Supplier-PUF-CY2012 ./data

3. Run script [data_chunker.py](./code/data_chunker.py) to chunk data-set

		$python data_chunker.py -i Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt

###III. IMPORT DATA CHUNK INTO DATABASES

1. Find and remove comment line from the top of data chunk1.txt that reads '0000000001      CPT copyright 2011 American Medical Association.  All Rights Reserved'.  

2. Run script [data_importer.py](./code/data_importer.py) to import first chunk of data into standalone and sharded cluster environments (update the file to reflect the credentials for your server connection):

		$python  data_importer.py -i chunk1.txt -s [setup]
		
			(where [setup] is 'standalone' or 'sharded')

###IV. EXECUTE PERFORMANCE SCRIPTS

1. Run script [performance_tester.py](./code/performance_tester.py) to record performance of the aggregate query on Standalone VM, and aggregate and mapreduce queries in the Sharded Cluster environment.  

		$python  performance_tester.py -s [setup] -q [query]
		
			(where [setup] is 'standalone' or 'sharded'; [query] is 'aggregate' or 'mapreduce')
			
    N.B. The mapreduce query, by virtue of its architecture, only runs in the sharded (distributed database) environment.
    
###V. REPEAT III AND IV

1. Copy 'headerline' from chunk1.txt and past in each subsequent chunk for importation. If first data line in chunk is incomplete due to chunking trancation, remove the line from the file.

2. Repeat III and IV above to increment size of data set and establish perfomrmance metrics at each stage  

###VI. VISUALIZE PERFORMANCE RESULTS

    Performance results are written to the 'performance_metrics' mongodb collection of the queried database and to the 'metrics.csv' file. Extract and plot results on graph 

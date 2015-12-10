#INSTRUCTIONS:

I. 	Set up server environments<br>
II.	Download and chunk data-set<br> 
III 	Import data chunk into databases<br>
IV.	Execute performance scripts<br>
V	Repeat III and IV to increment data-set sizes and execute performance scripts<br>
VI.	Vizualize performance results<br>


###I. SET UP SERVER ENVIRONMENTS	

####Set Up 1: Standalone VM

1. Spin up Openstack VM and install Cloudmesh using the instructions found here: [Quickstart for an Openstack VM](http://cloudmesh.github.io/introduction_to_cloud_computing/cloudmesh/setup/setup_openstack.html). Skip 2 and 3 below and [follow these instructions](https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/) if unable to successfully install Cloudmesh on the Openstack VM.
 
2. Run script vm_standalone_builder.py to create a VM for housing the stand-alone MongoDB database

3. Install the latest stable version of MongoDB on the VM created by issuing the commands:
	
		$ sudo apt-get update
		$ sudo apt-get install -y mongodb-org

4. Start the MongoDB server by issuing the command below:

		$ sudo service mongod start

5. Start the mongos server by issuing the command:
		$ mongo --host [name of the MongoDB server]


####Set Up 2: 3 VM Cluster

1. Install Cloudmesh on VM using the instructions found here:  [Quickstart for an Openstack VM](http://cloudmesh.github.io/introduction_to_cloud_computing/cloudmesh/setup/setup_openstack.html) . The server running Cloudmesh will serve as the mongos (router) server. Alternatively, reuse the router server set-up in 1 above as the mongos server to the distributed MongoDB cluster. Skip 2 and 3 below and [follow these instructions to install MongoDB on Ubuntu](https://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/) if unable to successfully install Cloudmesh on the Openstack VM.

2. From the mongos, run the script vm_cluster_builder.py to create a 3 node cluster for hosting the sharded MongoDB. 

3. Install the latest stable version of MongoDB on the VMs created by issuing the commands:
	
		$ sudo apt-get update
		$ sudo apt-get install -y mongodb-org

4. Generate a keyFile for use with server authentication within the cluster by running the openssl command: 

		$ openssl rand -base64 741 > mongodb-keyfile

   The above will ensure that the keyFile created is long and random, and only contains characters in base64 set, as is required by MongoDB for key files. 

5. Restrict permissions on the keyFile to the MongoDB owner by issuing the command:

		$ chmod 600 mongodb-keyfile 

6. Copy the file keyfile, mongodb-keyfile, to all servers in the set-up, including the mongos server. Create and place the keyfile in an obscure directory/path with permissions set to where it is readable by the MongoDB owner.

7. Update the provided sample yaml files mongos.conf, configsvr.conf and shardsvr.conf files with the correct path to the mongodb-keyfile on each server (find lines with place-holding text for the keyfile path).

8. Create data directories on each of the three cluster servers and ensure that the account running MongoDB has read and write access to them.

		$ mkdir /data/configdb

9. Place the mongos.conf file in the /etc folder of the mongos server. 

10. Place the configsvr.conf file in an appropriate folder e.g. /svr/mongodb  on each of the servers with the MongoDB cluster ‘configsvr’ role.
 
11. Place the shardsvr.conf file in the /svr/mongodb folder of each of the servers with the shard/database role (see configuration diagram above). 

12. Ensure that the permissions on the conf files are restricted but set to where they can be read by the account under which the MongoDB services run. 

###II. DOWNLOAD AND CHUNK DATA-SET

1. Download the tab delimited ['Medicare Provider Data - Physicians and Other Suppliers'](http://www.cms.gov/apps/ama/license-2011.asp?file=http://download.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/Medicare-Provider-Charge-Data/Downloads/Medicare-Physician-and-Other-Supplier-PUF-CY2012.zip) dataset archive file from Data.gov. 

2. Extract the dataset file from the archive and move it into the cloned ./data folder

		$unzip .../Medicare-Physician-and-Other-Supplier-PUF-CY2012.zip
		$mv .../Medicare-Physician-and-Other-Supplier-PUF-CY2012 ./data

3. Run script [data_chunker.py](./code/data_chunker.py) to chunk data-set

		$python data_chunker.py -i Medicare-Physician-and-Other-Supplier-PUF-CY2012.txt

###III. IMPORT DATA CHUNK INTO DATABASES

1. Run script [data_importer.py](./code/data_importer.py) to import first chunks on data into standalone and sharded cluster environments 

###IV. EXECUTE PERFORMANCE SCRIPTS


###V. REPEAT III AND IV


###VI. VISUALIZE PERFORMANCE RESULTS

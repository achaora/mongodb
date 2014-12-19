import cloudmesh
from pprint import pprint

#use mongo option for storage of basic information for use with cm
mesh = cloudmesh.mesh("mongo")

#get username and activate account
username = cloudmesh.load().username()
mesh.activate(username)

#register cloud
cloudmesh.shell("cloud on india")

#cache fresh images and flavors with refresh from india
mesh.refresh(username,types=['flavors', 'images'],names=["india"])

#select image and flavor
image = mesh.image('india', 'futuregrid/ubuntu-14.04')
flavor = mesh.flavor('india', 'm1.medium')
cloud =  "india"
#start vm
result = mesh.start(cloud=cloud,
                    cm_user_id=username,
                    flavor=flavor,
                    image=image)
                    
#assign public ip
server = result['server']['id']
ip=mesh.assign_public_ip('india', server, username)

#delay for ip assignment then ssh into machine
while True:
    result = mesh.wait(ipaddr=ip, interval=2, retry=10)
    if result == True:
        mesh.ssh_execute(ipaddr=ip, command="uname -a")
        break
    
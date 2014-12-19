import cloudmesh

#use India cloud
print cloudmesh.shell("cloud select india")

#activate the cloud, e.g.
print cloudmesh.shell("cloud on india")

#specify default key in cm for starting VMs
#*** - ADD input for specifying cloundmesh key
print cloudmesh.shell("key default"+ cmesh-key)

#seed name for VM cluster prefixes
#*** - ADD input for vm prifixes

print cloudmesh.shell("label --prefix=test --id=1")

#assign image and flavor of VMs
print cloudmesh.shell("default image --name=futuregrid/ubuntu-14.04")
print cloudmesh.shell("default flavor --name=m1.small")

#assign login name for machines, cluster name and number of machines  and start cluster of 3 servers
#*** - ADD input for login name

print cloudmesh.shell("cluster create --count=3 --group=test --ln=ubuntu")
You may also provide cloud name, flavor or image in the command if you don’t want to pre-set them. For example:

print cloudmesh.shell(“cluster create –count=3 –group=test0 –ln=ubuntu –cloud=india –flavor=m1.small –
image=futuregrid/ubuntu-14.04”)

#list machines in cluster
print cloudmesh.shell("vm list --refresh --group=test")

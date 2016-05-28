#!/bin/bash

####
##  sed 's/"vcenter":{.*\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"},/&"psc":{"ip":"10.62.92.100"},/' config.json
#   

config_json=/var/lib/vmware-marvin/config.json
psc_ip=10.62.92.56

# Change version 3.0.0 to 3.5.0
sed -i 's/"version":"3.5.0"/"version":"3.0.0"/' $config_json

# Add psc ip address at network attribute
#sed -i 's/"vcenter":{.*\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"},/&"psc":{"ip":"'$psc_ip'"},/' config.json
sed -i 's/"evorail":{"ip"/"psc":{"ip":"'$psc_ip'"},&/' config.json

# Add psc host name at hostnames attribute
domain_name=`dig +short -x $psc_ip`
name_array=(${domain_name//./ })
sed -i 's/"evorail":"/"psc":"'${names[0]}'",&/' $config.json

# Add join vc to global attribute
sed -i 's/"loginsightServer":"\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"/&,"joinVC":false/' $config.json
#sed -i 's/"evorail":"/"psc":"'${names[0]}'",&/' $config.json
#sed 's/},\s\{0,\}"vendor"/,"joinVC":false&/' $config.json

# Add external vc attribute
external_vc='"externalVC":{"psc":"","vcenter":"","vcUsername":"","vcPassword":"","datacenterName":"","clusterName":""},'
sed -i 's/"vendor"/'$external_vc'&/' $config.json



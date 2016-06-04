#!/bin/bash

config_json=/var/lib/vmware-marvin/config.json
psc_ip=10.62.92.56

# Change version 3.0.0 to 3.5.0
if_exist=`grep '"version":"3.5.0"' $config.json`
if [ -z $if_exist ]
then
	sed -i 's/"version":"3.5.0"/"version":"3.0.0"/' $config_json
fi

# Add psc ip address at network attribute
#sed -i 's/"vcenter":{.*\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"},/&"psc":{"ip":"'$psc_ip'"},/' config.json
if_exist=`grep '"psc":{"ip":"'$psc_ip'"}' $config.json`
if [ "${if_exist:-0}" == 0 ]
then
	sed -i 's/"evorail":{"ip"/"psc":{"ip":"'$psc_ip'"},&/' config.json
fi

# Add psc host name at hostnames attribute
domain_name=`dig +short -x $psc_ip`
name_array=(${domain_name//./ })
if_exist=`grep '"psc":"'${names[0]}'"' $config.json`
if [ -z $if_exist ]
then
	sed -i 's/"evorail":"/"psc":"'${names[0]}'",&/' $config.json
fi
# Add join vc to global attribute
if_exist=`grep '"joinVC":false' $config.json`
if [ -z $if_exist ]
then
	#sed -i 's/"loginsightServer":"\([0-9]\{1,3\}\.\)\{3\}[0-9]\{1,3\}"/&,"joinVC":false/' $config.json
	sed -i 's/"loginsightServer"/"joinVC":false,&/' $config.json
fi

# Add external vc attribute
if_exist=`grep 'externalVC' $config.json`
if [ -z $if_exist ]
then
	external_vc='"externalVC":{"psc":"","vcenter":"","vcUsername":"","vcPassword":"","datacenterName":"","clusterName":""},'
	sed -i 's/"vendor"/'$external_vc'&/' $config.json
fi


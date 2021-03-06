#/bin/bash

prefix_psc=data.vcenter.pscHost
runtime_properties=/var/lib/vmware-marvin/runtime.properties
vc_address=`grep 'data.vcenter.address' /var/lib/vmware-marvin/runtime.properties  | awk -F '=' '{print $2}'`
python_lib=/usr/lib/vmware-marvin/marvind/webapps/ROOT/WEB-INF/classes/scripts/lib/python2.7/
restore_to=/mystic
config_json=/var/lib/vmware-marvin/config.json

saveDB() {
	psql -U postgres mysticmanager -c "update settings set psc_ip='$1' where id='MysticManager';"
	if [ $? -ne 0 ]; then
		echo "Failed to update pscIp in DB, exit"
		exit 1
	else
		echo "DB update succeeds with pscIp"
	fi
}

saveRuntime() {
	sed -i "/^$prefix_psc=/c$prefix_psc=$1" $runtime_properties
}

decryptPwd() {
	encryptPwd=`cat $restore_to/encrypt_vcrootpw`
	outputFile="output.txt"
	export PATH=$PATH:/usr/java/jre-vmware/bin
        java -cp EncryMain.jar -jar EncryMain.jar $encryptPwd $outputFile
}

generateConfigFile() {
	echo "vc_url=$vc_address" > config.properties
	echo "vc_user=root" >> config.properties
	vcPwd=`cat output.txt`
	echo "vc_password=$vcPwd" >> config.properties
}

removeConfigFile() {
	rm -f config.properties
	rm -f output.txt
}

addDvsValue() {
	python add_dvs_value.py
}

importVcCert() {
	java -cp importcert-3.5.0.jar com.vmware.mystic.utils.ImportCertMain $vc_address
	chown -R tcserver:pivotal /var/lib/vmware-marvin/trust
}

editConfigJson() {
	# Change version 3.0.0 to 3.5.0
	if_exist=`grep '"version":"3.5.0"' $config_json`
	if [ -z $if_exist ]
	then
		sed -i 's/"version":"3.5.0"/"version":"3.0.0"/' $config_json
	fi
	
	# Add psc ip address at network attribute
	if_exist=`grep '"psc":{"ip":"'$1'"}' $config.json`
	if [ "${if_exist:-0}" == 0 ]
	then
		sed -i 's/"evorail":{"ip"/"psc":{"ip":"'$1'"},&/' $config_json
	fi
	
	# Add psc host name at hostnames attribute
	domain_name=`dig +short -x $1`
	name_array=(${domain_name//./ })
	if_exist=`grep '"psc":"'${names[0]}'"' $config_json`
	if [ -z $if_exist ]
	then
		sed -i 's/"evorail":"/"psc":"'${names[0]}'",&/' $config_json
	fi
	
	# Add join vc to global attribute
	if_exist=`grep '"joinVC":false' $config_json`
	if [ -z $if_exist ]
	then
		sed -i 's/"loginsightServer"/"joinVC":false,&/' $config_json
	fi
	
	# Add external vc attribute
	if_exist=`grep 'externalVC' $config_json`
	if [ -z $if_exist ]
	then
		external_vc='"externalVC":{"psc":"","vcenter":"","vcUsername":"","vcPassword":"","datacenterName":"","clusterName":""},'
		sed -i 's/"vendor"/'$external_vc'&/' $config_json
	fi
}

main() {
	echo -e " Please input the PSC IP address: "
	read pscIp
	saveDB $pscIp
	saveRuntime $pscIp

	echo " Configure Dvs information"
	decryptPwd
	generateConfigFile
	addDvsValue

	echo " Add psc info to config.json file"
	editConfigJson
	
	importVcCert
	removeConfigFile
	echo " PSC Update succeeds"
}

main

exit 0

#/bin/bash

prefix_psc=data.vcenter.pscHost
runtime_properties=/var/lib/vmware-marvin/runtime.properties
vc_address=`grep 'data.vcenter.address' /var/lib/vmware-marvin/runtime.properties  | awk -F '=' '{print $2}'`
python_lib=/usr/lib/vmware-marvin/marvind/webapps/ROOT/WEB-INF/classes/scripts/lib/python2.7/
restore_to=/mystic

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
	sed -i "/$prefix_psc/=/=$1/g" $runtime_properties
}

decryptPwd() {
	encryptPwd=`cat $restore_to/encrypt_vcrootpw`
	output="output.txt"
	export PATH=$PATH:/usr/java/jre-vmware/bin
	java -cp EncryMain.jar -jar EncryMain.jar $encryptPwd $output
}

generateConfigFile() {
	echo "vc_url=$vc_address" > config.properties
	echo "vc_user=root" >> config.properties
	vcPwd=`cat output.txt`
	echo "vc_password=$vcPwd" >> config.properties
}

importVcCert() {
	java -cp importcert-3.5.0.jar com.vmware.mystic.utils.ImportCertMain $vc_address
}

removeConfigFile() {
	rm -f config.properties
	rm -f output.txt
}

addDvsValue() {
	#ln -s $python_lib ./python_lib
	python add_dvs_value.py
}

main() {
	echo -e " Please input the PSC IP address: "
	read pscIp
	saveDB $pscIp
	saveRuntime $pscIp
	
	decryptPwd
	generateConfigFile
	addDvsValue
	
	removeConfigFile
	echo "PSC update succeeds"
}

main

exit 0

#/bin/bash

restore_from=/home/mystic/restore
restore_to=/mystic
upgrade_version=9
python_lib=/usr/lib/vmware-marvin/marvind/webapps/ROOT/WEB-INF/classes/scripts/lib/python2.7/
vc_address=`grep 'data.vcenter.address' /var/lib/vmware-marvin/runtime.properties  | awk -F '=' '{print $2}'`
management_username=`grep 'data.managementUsername' /var/lib/vmware-marvin/runtime.properties  | awk -F '=' '{print $2}'`
management_password=`grep 'data.managementPassword' /var/lib/vmware-marvin/runtime.properties  | awk -F '=' '{print $2}'`

init() {
	if [ ! -d $restore_from ]; then
		mkdir "$restore_from"
	fi

	if [ $? -ne 0 ]; then
		echo "Failed to create restore folder, exit"
		exit 1
	fi
}

uncompressData() {
	tar -xvf ${restore_from/restore/}backup_data.tar -C $restore_from
	if [ $? -ne 0 ]; then
		echo "Failed to uncompress the backup, exit"
		exit 1
	fi
}

copyProperties() {
	cp -rf $restore_from/$1 $restore_to/
	if [ $? -ne 0 ]; then
		echo "Failed to copy properties, exit"
		exit 1
	fi
}

generateConfigFile() {
	echo "vc_url=$vc_address" > config.properties
	echo "vc_user=root" >> config.properties
	vcPwd=`cat $restore_to/output.txt`
	echo "vc_password=$vcPwd" >> config.properties
	echo "service_user=service" >> config.properties
	echo "service_pwd=Password123!" >> config.properties
	echo "management_user=${management_username}" >> config.properties
	echo "management_pwd=$management_password" >> config.properties
}

decryptPwd() {
	encryptPwd=`cat $restore_to/encrypt_vcrootpw`
	output="$restore_to/output.txt"
	export PATH=$PATH:/usr/java/jre-vmware/bin
	java -cp EncryMain.jar -jar EncryMain.jar $encryptPwd $output
}

removeConfigFile() {
	rm -f config.properties
	rm -f $restore_to/output.txt
}

restoreDB() {
	psql -U postgres mysticmanager -c "DROP SCHEMA IF EXISTS public CASCADE;"
	psql -U postgres mysticmanager -c "CREATE SCHEMA public;"
	gunzip -c $restore_from/backup_mm.gz | psql -U postgres mysticmanager
	if [ $? -ne 0 ]; then
		echo "Failed to restore DB, exit"
		exit 1
	fi
}

upgradeDB() {
	psql -U postgres mysticmanager -c "SELECT COUNT(*) from settings;" | awk '{if(NR==3) print $1}'
	if [ $? -ne 0 ]; then
		echo "Failed to get settings count, exit"
		exit 1
	fi
	let count=`psql -U postgres mysticmanager -c "SELECT COUNT(*) from settings;" | awk '{if(NR==3) print $1}'`

	psql -U postgres mysticmanager -c "SELECT db_version FROM settings;"
	if [ $? -ne 0 ]; then
		echo "DB version before 0, set to 0"
		let db_version=0
	else
		let db_version=`psql -U postgres mysticmanager -c "SELECT db_version FROM settings;" | awk '{if(NR==3) print $1}'`
		if [ $? -ne 0 ]; then
			echo "DB version missing, exit"
			exit 1
		fi
	fi

	for((i=$db_version+1;i<=$upgrade_version;i++))
	do
		echo "Upgrade to version $i"
		psql -U postgres mysticmanager -f ./sql/mystic_delta.$i.sql
		if [ $? -ne 0 ]; then
			echo "Upgrade DB failed, exit"
			exit 1
		fi
	done
	
	tables="dimm disk nic board sata_dom esx node power_supply chassis appliance syr_configuration connect_home_message mystic_event"
	for table in $tables
	do
		psql -U postgres mysticmanager -c "delete from $table;"
		if [ $? -ne 0 ]; then
			echo "Failed to delete data from $table, exit"
			exit 1
		else
			echo "Delete data from $table successfully"
		fi
	done
}

upgradeEsxiUser() {
	ln -s $python_lib ./python_lib
	python upgrade_esxi_user.py
	if [ $? -ne 0 ];then
		echo "Upgrade ESXi user failed, exit"
		exit 1
	fi
}

main() {
	service vmware-marvin stop
	service runjars stop
	init
	echo "Step1: Create the restore folder $restore_from successfully"
	uncompressData
	echo "Step2: Uncompress the backup to restore folder $restore_from successfully"
	cp -f $restore_from/resolv.conf /etc
	if [ $? -ne 0 ]; then
		echo "Failed to copy resolv.conf to /etc, exit"
		exit 1
	else
		echo "Step3: Restore resolv.conf successfully"
	fi
	copyProperties encrypt_key.properties
	echo "Step4: Restore encrypt_key.properties successfully"
	copyProperties encrypt_vcrootpw
	echo "Step5: Restore encrypt_vcrootpw successfully"
	copyProperties suppress.properties
	echo "Step6: Restore suppress.properties successfully"
	decryptPwd
	generateConfigFile
	restoreDB
	echo "Step7: Restore database successfully"
	upgradeDB
	echo "Step8: Upgrade database successfully"
	upgradeEsxiUser
	echo "Step9: Upgrade ESXi user successfully"
	removeConfigFile
	echo "Step10: Remove temporary files successfully"
	service vmware-marvin start
	service runjars start
	echo "Restore succeeds!"
}

main


exit 0


#/bin/bash

restore_from=/home/mystic/restore
restore_to=/mystic
upgrade_version=9

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
}

copyProperties() {
    cp -rf $restore_from/$1 $restore_to/
    if [ $? -ne 0 ]; then
        echo "Failed to copy properties, exit"
        exit 1
    fi
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
		psql -U postgres mysticmanager -f ./mystic_delta.$i.sql
		if [ $? -ne 0 ]; then
			echo "Upgrade DB failed, exit"
			exit 1
		fi
	done
}

upgradeEsxiUser() {
	python upgrade_esxi_user.py
	if [ $?==0 ];then
		echo "Upgrade Esxi user failed, exit"
    	exit 1
	fi
}

main() {
    init
	uncompressData
    copyProperties encrypt_key.properties
    copyProperties suppress.properties
    restoreDB
	upgradeDB
	upgradeEsxiUser
}

main


exit 0


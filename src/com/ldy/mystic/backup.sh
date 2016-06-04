#/bin/bash

backup_from=/mystic
backup_to=/home/mystic/backup/data
# lite/full
log_type=lite
log_name=mystic_lite_log

init() {
    if [ ! -d $backup_to ]; then
        mkdir -p "$backup_to"
    else
        rm -fr $backup_to/*
    fi

    if [ $? -ne 0 ]; then
        echo "Failed to create backup folder, exit"
        exit 1
    fi
}

copyProperties() {
    cp -rf $1 $backup_to/
    if [ $? -ne 0 ]; then
        echo "Failed to copy properties, exit"
        exit 1
    fi
    echo " The file $1 is copied successful."
}

backupDB() {
    pg_dump -U postgres mysticmanager | gzip > $backup_to/backup_mm.gz
    if [ $? -ne 0 ]; then
        echo "Failed to backup DB, exit"
        exit 1
    fi
}

compressData() {
    cd $backup_to
    tar -cf ../backup_data.tar *
}

runlog() {
    echo -e " Are you want to export full logs, this will run mysticDC.sh(y/n)?"
    read answer
    if [ $answer = y -o $answer = Y ]; then
        ./mysticDC.sh $log_type $log_name
        cp -f /tmp/mystic/dc/$log_name $backup_to
    fi

    if [ $? -ne 0 ]; then
        echo "Failed to run log, exit"
        exit 1
    fi
}

main() {
    init
    echo "Step1: Create the backup folder successful, path is ${backup_to/data}"
    copyProperties /etc/resolv.conf
    copyProperties $backup_from/encrypt_key.properties
    copyProperties $backup_from/encrypt_vcrootpw
    copyProperties $backup_from/suppress.properties
    echo "Step2: Copy property file successful. "
    backupDB
    echo "Step3: DB backup successful."
    runlog

    compressData
    echo "Step4: Backup file generated successfully, please get the backup_data.tar at ${backup_to/data/}"
}

main


exit 0


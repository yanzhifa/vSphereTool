#///////////////////////////////////////////////////////////////////////
#/// Copyright (C) 2015, All Rights Reserved, by
#/// EMC Corporation, Hopkinton MA.
#///
#/// This software is furnished under a license and may be used and copied
#/// only  in  accordance  with  the  terms  of such  license and with the
#/// inclusion of the above copyright notice. This software or  any  other
#/// copies thereof may not be provided or otherwise made available to any
#/// other person. No title to and ownership of  the  software  is  hereby
#/// transferred.
#///
#/// The information in this software is subject to change without  notice
#/// and  should  not be  construed  as  a commitment by EMC Corporation.
#///
#/// EMC assumes no responsibility for the use or  reliability of its
#/// software on equipment which is not supplied by EMC.
#/////////////////////////////////////////////////////////////////////////
#!/bin/bash

# set -x

doCopy() {
    mkdir -p $dc_dir/$2
    cp -rf $1 $dc_dir/$2
}

doExec() {
    mkdir -p $dc_dir/$2
    touch $dc_dir/$2/$3
    $1 > $dc_dir/$2/$3
}

preparation() {
    dc_log=/var/log/mystic/dc.log
    if [[ -f $dc_log ]]; then
        logSize=`du -m $dc_log | cut -f1`
        echo "Log size: $logSize MB" >> $dc_log
        if [[ $logSize > 10 ]]; then
            echo "" > $dc_log
        fi
    fi

    echo "---------------------------------------------------------------" >> $dc_log
    echo "Data collection started at: " `date` >> $dc_log
    mkdir -p /tmp/mystic/dc
    chmod 777 /tmp/mystic/dc
    rm -rf /tmp/mystic/dc/*
    dt=`date +%F_%H_%M_%S`
    dc_dir=/tmp/mystic/dc/mystic_manager_data_collection_$dt
    mkdir $dc_dir
    echo "Created directory $dc_dir" >> $dc_log
}

generateFullLogBundle() {

    generateLiteLogBundle

    #events
    doCopy '/tmp/mystic/events.csv' 'events'
    #postgresql dump
    doExec 'pg_dump -U postgres mysticmanager' 'dump' 'db_mysticmanager'

}




generateLiteLogBundle() {
    # All Logs
    doCopy '/var/log/mystic/*' 'logs/mystic'
    doCopy '/var/log/rabbitmq/*' 'logs/rabbitmq'
    doCopy '/mystic/apache-tomcat/logs/*' 'logs/apache-tomcat'
    doCopy '/var/log/*.log' 'logs'
    doCopy '/var/log/messages*' 'logs'
    doCopy '/var/log/mail*' 'logs'


    # Mystic data
    doCopy '/tmp/mystic/data/*' 'data'

    # Mystic configuration files
    doCopy '/mystic/apache-tomcat/webapps/ROOT/version' 'conf'
    doCopy '/mystic/apache-tomcat/webapps/ROOT/WEB-INF/*.xml' 'conf/apache-tomcat'

    # System configuration files
    doCopy '/etc/resolv.conf' 'conf/etc'


    # System command output
    doExec 'ip addr' 'cmd' 'ip_addr'
    doExec 'ip route' 'cmd' 'ip_route'
    doExec 'uname -a' 'cmd' 'uname'
    doExec 'ps aux' 'cmd' 'ps'
    doExec 'netstat -anp' 'cmd' 'netstat'
    doExec 'df -h' 'cmd' 'disk'

    # rabbitmq command output
    doExec 'rabbitmqctl list_queues' 'cmd/rabbitmq' 'list_queues'
    doExec 'rabbitmqctl list_exchanges' 'cmd/rabbitmq' 'list_exchanges'
    doExec 'rabbitmqctl list_connections' 'cmd/rabbitmq' 'list_connections'
}


bundleFiles()
{
    echo `ls -l $dc_dir` >> $dc_log

    cd /tmp/mystic/dc
    targetFile=mystic_manager_data_collection_tmp_$dt'.tar.gz'
    tar -zcvf $targetFile mystic_manager_data_collection_$dt >> $dc_log 2>&1

    mv $targetFile $1

    echo $dc_dir".tar.gz" >> $dc_log
    echo "/tmp/mystic/dc/$1">/tmp/mystic/dc/.output
    chmod -R 744 /tmp/mystic/dc/$1
    chown -R mystic:users /tmp/mystic/dc/$1
}

usage()
{
    echo "Usage: $0 lite|full <filename>"
}


main()
{
    if [ $# -ne 2 ]; then
    echo $#
        usage;
    elif [ $1 == 'lite' ]; then
        generateLiteLogBundle;
        bundleFiles $2
    elif [ $1 == 'full' ]; then
        generateFullLogBundle;
        bundleFiles $2
    else
        usage;
    fi

}

preparation
main $@




exit 0

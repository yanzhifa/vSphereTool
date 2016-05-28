#!/bin/bash

ghent_json=""
old_data=`cat /var/lib/vmware-marvin/hosts.json`
array=(${old_data//\},/ })
count=`expr ${#array[@]} - 1`

for((i=0;i<=$count;i++))
do
    asset_tag=`echo ${array[$i]} | awk -F ',' '{print $1}' | awk -F ':' '{print $2}'`
    new_asset_tag=${asset_tag/-/-${asset_tag:`awk 'BEGIN{print index('$asset_tag',"-")-2}'`:2}-}
    new_node=${array[$i]/$asset_tag/$new_asset_tag}
	
    marvin_list=$(echo ${new_asset_tag//\"/} | tr "-" "\n")
    app_id=`echo $marvin_list|cut -d ' ' -f 1`
    support_nodes=`echo $marvin_list|cut -d ' ' -f 2`
    position=`echo $marvin_list|cut -d ' ' -f 3`
    
    support_nodes=`expr $support_nodes + 0`
    position=`expr $position + 0`
    
    if [ $i -lt $count ]
    then
        new_node=$new_node",\"marvinId\":{\"applianceId\":\"$app_id\",\"totalSupportedNodes\":$support_nodes,\"position\":$position},\"nodeVersionInfo\":null},"
    else
        new_node=${new_node/\}]/}",\"marvinId\":{\"applianceId\":\"$app_id\",\"totalSupportedNodes\":$support_nodes,\"position\":$position},\"nodeVersionInfo\":null}]"
    fi
    ghent_json=$ghent_json$new_node
	
done

echo $ghent_json > /var/lib/vmware-marvin/hosts.json

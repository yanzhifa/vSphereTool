#!/bin/bash

COUNTER=`cat /var/lib/vmware-marvin/hosts.json|./jq '. | length'`


ghent_json=""

for((i=0;i<$COUNTER;i++)) do
    json_node=`cat /var/lib/vmware-marvin/hosts.json|./jq -c '.['$i']'`
    assetTag=`./jq '.assetTag'<<<"$json_node"`
    new_node=${json_node/-/-${assetTag:`awk 'BEGIN{print index('$assetTag',"-")-2}'`:2}-}
	new_asset_tag=`./jq -c '.assetTag'<<<"$new_node"`

	marvin_list=$(echo ${new_asset_tag//\"/} | tr "-" "\n")
    app_id=`echo $marvin_list|cut -d ' ' -f 1`
    support_nodes=`echo $marvin_list|cut -d ' ' -f 2`
    position=`echo $marvin_list|cut -d ' ' -f 3`
    support_nodes=`expr $support_nodes + 0`
    position=`expr $position + 0`

    new_attribute="{\"applianceId\":\"$app_id\",\"totalSupportedNodes\":$support_nodes,\"position\":$position}"
    json_node=`./jq -c '. + { "marvinId":'$new_attribute' } + {"nodeVersionInfo":null}' <<<"$json_node"`
	assetTag=${assetTag//\"/}
    json_node=${json_node/${assetTag}/$new_asset_tag}
	
	if [ -z $ghent_json ]
	then
		ghent_json="["$ghent_json$json_node
	else
		ghent_json=$ghent_json","$json_node
	fi

done
ghent_json=$ghent_json"]"
echo $ghent_json > /var/lib/vmware-marvin/host_test.json

rm -f /var/lib/vmware-marvin/hosts.json
mv /var/lib/vmware-marvin/host_test.json /var/lib/vmware-marvin/hosts.json

#!/bin/bash

COUNTER=`cat hosts.json|./jq '. | length'`

ghent_json=""

for((i=0;i<$COUNTER;i++)) do
     json_node=`cat hosts.json|./jq -c '.['$i']'`
     echo $json_node
     assetTag=`./jq '.assetTag'<<<"$json_node"`
     echo $assetTag
     
     new_node=${json_node/-/-${assetTag:`awk 'BEGIN{print index('$assetTag',"-")-2}'`:2}-}
	 echo $new_node
     new_asset_tag=`./jq -c '.assetTag'<<<"$new_node"`
     new_asset_tag=${new_asset_tag//\"/}
     
	 
	 marvin_list=$(echo ${new_asset_tag//\"/} | tr "-" "\n")
     app_id=`echo $marvin_list|cut -d ' ' -f 1`
     support_nodes=`echo $marvin_list|cut -d ' ' -f 2`
     position=`echo $marvin_list|cut -d ' ' -f 3`
     echo $position
     
     support_nodes=`expr $support_nodes + 0`
     position=`expr $position + 0`
     echo $support_nodes $position $app_id
     
     new_attribute="{\"applianceId\":\"$app_id\",\"totalSupportedNodes\":$support_nodes,\"position\":$position}"
     echo $new_attribute
	 
     json_node=`./jq -c '. + { "marvinId":'$new_attribute' } + {"nodeVersionInfo":null}' <<<"$json_node"`
     echo $json_node
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
echo $ghent_json > host_test.json

rm -f hosts.json
mv host_test.json hosts.json


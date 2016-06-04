
import json
from collections import OrderedDict

with open('config.json') as f:
	data=f.read()
	jsondata=json.loads(data, object_pairs_hook=OrderedDict)
print jsondata['network']['vcenter']
print jsondata['network']
print jsondata['version']

jsondata['version']='3.5.0'
jsondata['network']['psc']={'ip':'10.10.10.10'}
#jsondata['network'].psc="{'ip':'10.10.10.10'}"
print jsondata['network']
json_encode=json.dumps(jsondata, separators=(',', ':'))
print json_encode

#with open('config.json') as f:
#	jsondata = json.load(f)
#print jsondata

#f=open("config.json","r")
#s=f.read
#print s

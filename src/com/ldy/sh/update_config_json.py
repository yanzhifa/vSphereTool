#!/usr/bin/env python

"""
Upgrade Bretton Woods to Ghent
"""
import os, sys
from test.test_ssl import data_file
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "lib/")))

import json
from pprint import pprint

def main():
    #with open('config_ori.json') as data_file:
    #    data = json.load(data_file)
    #pprint(data)
    
    json_data=open('config_ori.json').read()

    data = json.loads(json_data)
    pprint(data)

# Start program
if __name__ == "__main__":
    main()

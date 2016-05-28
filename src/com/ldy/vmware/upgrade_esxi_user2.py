#!/usr/bin/env python

"""
Upgrade Bretton Woods to Ghent
"""

import subprocess

update_sql = '''psql -U postgres mysticmanager -c \"update settings set management_user='manageuser@localos',  management_password='P@ssw0rd', cluster_name='MARVIN-Virtual-SAN-Cluster-94f23197-731d-4a22-a468-2cd68ccd1b18' where id='MysticManager';\"'''
subprocess.call(update_sql, shell=True)

"psql -U postgres mysticmanager -c \"update settings set management_user='{0}',  management_password='{1}', cluster_name='{2}' where id='MysticManager';\""
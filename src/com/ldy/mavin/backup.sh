#!/bin/bash

# Stop relevant services.
/etc/init.d/vmware-marvin stop
/etc/init.d/vmware-loudmouth stop

# Backup MARVIN related configuration files.
tar czf bw-etc-vmware-marvin.tgz /etc/vmware-marvin/
tar czf bw-var-lib-vmware-marvin.tgz /var/lib/vmware-marvin/


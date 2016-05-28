#!/bin/bash

# NOTE:
# We purposefully do *not* clean up the files after we complete the upgrade to
# let whomever is performing the upgrade make sure things work before they clean
# up.

RESTORE_STAGE="bw-vmware-marvin-restore"

# Make sure the services are stopped
systemctl stop vmware-marvin.service
systemctl stop vmware-loudmouth.service

mkdir -p ${RESTORE_STAGE}

# Create backups of the current running config.
tar czf ghent-etc-vmware-marvin.tgz /etc/vmware-marvin/
tar czf ghent-var-lib-vmware-marvin.tgz /var/lib/vmware-marvin/

# Make sure the locations where we want to populate are empty.
rm -rf /var/lib/vmware-marvin/*

# Unpack the backup files.
tar xzf bw-etc-vmware-marvin.tgz -C ${RESTORE_STAGE}
tar xzf bw-var-lib-vmware-marvin.tgz -C ${RESTORE_STAGE}

# Don't overwrite the following files.
rm ${RESTORE_STAGE}/etc/vmware-marvin/tomcat-catalina-opts.cfg

# Remove any cached files.
rm ${RESTORE_STAGE}/var/lib/vmware-marvin/*.data
rm ${RESTORE_STAGE}/var/lib/vmware-marvin/config-journal.json

# Restore the configuration
cp -p -R ${RESTORE_STAGE}/etc/vmware-marvin/* /etc/vmware-marvin/
cp -p -R ${RESTORE_STAGE}/var/lib/vmware-marvin/* /var/lib/vmware-marvin/

# Update hosts.json
./update_hosts_json.sh

# Shove in any additional key/value pairs that we rely on.
# XXX: TODO: We need to populate the "data.moref.dvs" field at some point if we
# want expansion to work.
cat > /var/lib/vmware-marvin/runtime.properties << EOF
data.joinExternalVC=
data.vcenter.pscHost=
data.moref.dvs=
EOF

# Launch services
systemctl start vmware-loudmouth.service
systemctl start vmware-marvin.service


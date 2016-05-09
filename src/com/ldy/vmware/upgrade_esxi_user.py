#!/usr/bin/env python

"""
Upgrade Bretton Woods to Ghent 
"""
import ssl
import subprocess
import atexit
import requests
import ConfigParser

from pyVmomi import vim
from pyVmomi import vmodl
from pyVim import connect
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class FakeSecHead(object):
    def __init__(self, fp):
        self.fp = fp
        self.sechead = '[asection]\n'

    def readline(self):
        if self.sechead:
            try: 
                return self.sechead
            finally: 
                self.sechead = None
        else: 
            return self.fp.readline()

def connection(host_ip, username, password):
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE
        
    si = connect.SmartConnect(host=host_ip,
                              user=username,
                              pwd=password,
                              port=int("443"),
                              sslContext=context)
    return si

def disconnection(si):
    connect.Disconnect(si)
    si = None

"""
Get cluster name
"""
def get_cluster(content):
    cluster_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.ClusterComputeResource],
                                                           True)
    ds_cluster_list = cluster_view.view
    cluster_view.Destroy()
       
    for ds_cluster in ds_cluster_list:
        return ds_cluster.name
"""
Add management user and delete service user for all esxi host
"""
def user_oper(content, service_user, service_pwd, mgr_user, mgr_pwd):
    """
    Step1. Search DistributedVirtualPortgroup
    """
    portgroup_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                            [vim.dvs.DistributedVirtualPortgroup],
                                                            True)
    dc_portgroup_view = portgroup_view.view
    portgroup_view.Destroy()
    portgroup_key = None
    for portgroup in dc_portgroup_view:
        print("{}\t{}\t".format("ESXi Host:    ", portgroup.name))
        print("{}\t{}\t\n".format("ESXi key:    ", portgroup.key))
        if portgroup.name.startswith("Management Network") :
            portgroup_key = portgroup.key
    if not portgroup_key :
        print "Management Network portgroup is not found! "
        return -1
    
    """
    Step2. Add management user and delete service user for all esxi host
    """
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                      [vim.HostSystem],
                                                      True)
    esxi_hosts = host_view.view
    host_view.Destroy()

    for esxi_host in esxi_hosts:
        print("{}\t{}\t".format("ESXi Host:    ", esxi_host.name))
        vnics = esxi_host.config.network.vnic
        host_ip = None
        for vnic in vnics:
            if vnic.spec.distributedVirtualPort.portgroupKey == portgroup_key :
                host_ip = vnic.spec.ip.ipAddress

        si = connection(host_ip, service_user, service_pwd)
        if not si:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1
        print("{}\t{}\t".format("Connect host success:    ", host_ip))

        """
        Add management user
        """
        host_content = si.RetrieveContent()
        accountManager = host_content.accountManager
        newUser = vim.host.LocalAccountManager.AccountSpecification()
        newUser.id = mgr_user
        newUser.password = mgr_pwd
        accountManager.CreateUser(newUser)
        print("{}\t{}\t".format("Add new user success:    ", mgr_user))
        
        """
        Grant admin to management user
        """
        authManager = host_content.authorizationManager
        # get admin roleid
        roles = authManager.roleList
        adminRoleId = None
        for role in roles:
            if role.name == "Admin":
                adminRoleId = role.roleId
         
        entity = host_content.rootFolder
        permissions = []
        permission = vim.AuthorizationManager.Permission()
        permission.entity = entity
        permission.principal = mgr_user
        permission.group = False
        permission.roleId = adminRoleId
        permission.propagate = True
        permissions.append(permission)
        authManager.SetEntityPermissions(entity, permissions)
        print("{}\t{}\t".format("Grant admin to management user:    ", mgr_user))
        
        disconnection(si)
        
        """
        User the management user to login
        """
        si = connection(host_ip, mgr_user, mgr_pwd)
        print("{}\t{}\t".format("Relogin by management user:    ", mgr_user))
        """
        Delete service user
        """
        host_content = si.RetrieveContent()
        accountManager = host_content.accountManager
        accountManager.RemoveUser(service_user)
        print("{}\t{}\t".format("Delete service user success:    ", service_user))
        
        disconnection(si)
        print ("\n")

def main():

    try:
        cp = ConfigParser.SafeConfigParser()
        cp.readfp(FakeSecHead(open('./config.properties')))
        
        service_instance = connection(cp.get("asection", "vc_url"), cp.get("asection", "vc_user"), cp.get("asection", "vc_password"))

        if not service_instance:
            print("Could not connect to the specified host using "
                  "specified username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)
        content = service_instance.RetrieveContent()
        
        """
        Step1. Get cluster name
        """
        cluster_name = get_cluster(content)
        print("{}\t{}\t".format("Cluster Name:    ", cluster_name))
        
        """
        #Step2. Add management user, delete service user for all esxi hosts
        """
        manager_user = cp.get("asection", "management_user")
        manager_pwd = cp.get("asection", "management_pwd")
        user_oper(content, cp.get("asection", "service_user"), cp.get("asection", "service_pwd"), manager_user, manager_pwd)
        
        """
        #Step3. Update settings
        """
        update_sql = "psql -U postgres mysticmanager -c \"update settings set management_user='{0}',  management_password='{1}', cluster_name='{2}' where id='MysticManager';\""
        update_sql = update_sql.format(manager_user, manager_pwd, cluster_name)
        subprocess.call(update_sql, shell=True)

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

#!/usr/bin/env python
# William Lam
# www.virtuallyghetto.com

"""
vSphere Python SDK program for listing Datastores in Datastore Cluster
"""
import ssl
import atexit
import requests

from pyVmomi import vim
from pyVmomi import vmodl
from pyVim import connect

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#def connection():

def main():
    """
   Simple command-line program for listing Datastores in Datastore Cluster
   """

    try:
        
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        
        service_instance = connect.SmartConnect(host="10.62.92.54",
                                                user="administrator@vsphere.local",
                                                pwd="Testvxrail123!",
                                                port=int("443"),
                                                sslContext=context)
        if not service_instance:
            print("Could not connect to the specified host using "
                  "specified username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        
        """
        Step1. Search cluster
        """
        cluster_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                           [vim.ClusterComputeResource],
                                                           True)
        ds_cluster_list = cluster_view.view
        cluster_view.Destroy()
       
        for ds_cluster in ds_cluster_list:
            print "Cluster: " + ds_cluster.name
        
        """
        Step2. Search DistributedVirtualPortgroup
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
        Step3. Add management user and delete service user for all esxi host
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
                    print host_ip
                    
            si = connect.SmartConnect(host=host_ip,
                                      user="root",
                                      pwd="Testesx123!",
                                      port=int("443"),
                                      sslContext=context)
            if not si:
                print("Could not connect to the specified host using specified "
                      "username and password")
                return -1
            print "connect host success " + host_ip

            """
            Add management user
            """
            host_content = si.RetrieveContent()
            accountManager = host_content.accountManager
            newUser = vim.host.LocalAccountManager.AccountSpecification()
            newUser.id = "serviceuser"
            newUser.password = "P@ssw0rd"
            accountManager.CreateUser(newUser)
            print("{}\t{}\t".format("Add new user success:   ", "serviceuser"))
            
            """
            Grant role to user
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
            permission.principal = "serviceuser"
            permission.group = False
            permission.roleId = adminRoleId
            permission.propagate = True
            permissions.append(permission)
            authManager.SetEntityPermissions(entity, permissions)
            print ("grant role success")
            
            connect.Disconnect(si)
            si = None
            print ("\n")

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

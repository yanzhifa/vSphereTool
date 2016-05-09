#!/usr/bin/env python
# William Lam
# www.virtuallyghetto.com

"""
vSphere Python SDK program for listing all ESXi datastores and their
associated devices
"""
import argparse
import atexit
import json
import ssl

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim


def main():
    """
   Simple command-line program for listing all ESXi datastores and their
   associated devices
   """

    #args = get_args()

    #cli.prompt_for_password(args)

    import ssl
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.verify_mode = ssl.CERT_NONE

    try:
        service_instance = connect.SmartConnect(host="10.62.81.91",
                                                user="root",
                                                pwd="Password123!",
                                                port=int("443"),
                                                sslContext=context)
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        
        #accountManager = content.accountManager
        #newUser = vim.host.LocalAccountManager.AccountSpecification()
        #newUser.id = "testUser"
        #newUser.password = "1qaz@WSX"
        #accountManager.CreateUser(newUser)
        
        authManager = content.authorizationManager
        # step1 get roleid
        roles = authManager.roleList
        adminRoleId = None
        for role in roles:
            if role.name == "Admin":
                adminRoleId = role.roleId
         
        entity = content.rootFolder
        permissions = []
        permission = vim.AuthorizationManager.Permission()
        permission.entity = entity
        permission.principal = "testUser"
        permission.group = False
        permission.roleId = adminRoleId
        permission.propagate = True
        permissions.append(permission)
        authManager.SetEntityPermissions(entity, permissions)
        print ("grant role success")

        # Search for all ESXi hosts
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.HostSystem],
                                                          True)
        esxi_hosts = objview.view
        objview.Destroy()

        for esxi_host in esxi_hosts:
            print("{}\t{}\t\n".format("ESXi Host:    ", esxi_host.name))
            
        


    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

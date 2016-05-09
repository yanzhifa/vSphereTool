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
        service_instance = connect.SmartConnect(host="10.62.92.54",
                                                user="administrator@vsphere.local",
                                                pwd="Testvxrail123!",
                                                port=int("443"),
                                                sslContext=context)
        if not service_instance:
            print("Could not connect to the specified host using specified "
                  "username and password")
            return -1

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        # Search for all ESXi hosts
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.dvs.DistributedVirtualPortgroup],
                                                          True)
        portgroup_view = objview.view
        objview.Destroy()
        
        

        for portgroup in portgroup_view:
            print("{}\t{}\t\n".format("ESXi Host:    ", portgroup.name))
            print("{}\t{}\t\n".format("ESXi key:    ", portgroup.key))
            
        
        #objviewAccount = content.viewManager.CreateContainerView(content.rootFolder,
        #                                                  [vim.host.LocalAccountManager],
        #                                                  True)
        #accountManager = objviewAccount.view
        #objviewAccount.Destroy()
        #newUser = vim.host.LocalAccountManager.AccountSpecification()
        #newUser.id = "testUser"
        #newUser.password = "1qaz@WSX"
        #accountManager.CreateUser(newUser)


    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

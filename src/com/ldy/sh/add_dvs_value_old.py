#!/usr/bin/env python

"""
Upgrade Bretton Woods to Ghent
"""
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "lib/")))

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
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE

        si = connect.SmartConnect(host=host_ip,
                                  user=username,
                                  pwd=password,
                                  port=int("443"),
                                  sslContext=context)
        return si
    except Exception as e:
        print("Could not connect to the specified host using specified "
                  "username=" + username + " and password=" + password)
        return None

def disconnection(si):
    connect.Disconnect(si)
    si = None

def main():

    try:
        cp = ConfigParser.SafeConfigParser()
        cp.readfp(FakeSecHead(open('./config.properties')))
        
        service_instance = connection(cp.get("asection", "vc_url"), cp.get("asection", "vc_user"), cp.get("asection", "vc_password"))

        atexit.register(connect.Disconnect, service_instance)
        content = service_instance.RetrieveContent()

        """
        Search VmwareDistributedVirtualSwitch
        """
        dvs_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                                [vim.dvs.VmwareDistributedVirtualSwitch],
                                                                True)
        dvs_value = None
        for dvs in dvs_view.view:
            dvs_value = dvs._moId
            break

        dvs_view.Destroy()
        print dvs_value
        #dvs_sh_str = "sed -i \"/data.moref.dvs/s/=/={0}/g\" /var/lib/vmware-marvin/runtime.properties"
        #dvs_sh_str = "sed -ig \"/data.moref.dvs/s/=/={0}/g\" /Users/yanz3/runtime.properties"
        #dvs_sh_str = "sed -ig 's/^data\.moref.*/data\.moref\.dvs=dvs-24/g' /Users/yanz3/runtime.properties"
        dvs_sh_str = "sed -ig '/data.moref.dvs=/ s/=.*/={0}/' /Users/yanz3/runtime.properties"
        dvs_sh_str = dvs_sh_str.format(dvs_value)
        print dvs_sh_str
        subprocess.call(dvs_sh_str, shell=True)


    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

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
        Step1. Search DistributedVirtualPortgroup
        """
        cluster_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                              #[vim.ClusterComputeResource],
                                                              [vim.HostSystem],
                                                              True)
        dc_portgroup_view = cluster_view.view
        cluster_view.Destroy()
        host=None
        for portgroup in dc_portgroup_view:
            print("{}\t{}\t".format("ESXi Host:    ", portgroup.name))
            print("{}\t{}\t\n".format("ESXi key:    ", portgroup._moId))
            
            host=portgroup
            break

        cluster = host.parent
        distributepgs=cluster.environmentBrowser.QueryConfigTarget(host).distributedVirtualPortgroup
        portgroup_morid=None
        for pg in distributepgs:
            if pg.uplinkPortgroup == True:
                portgroup_morid = pg.portgroupKey
                continue

        for portgroup in cluster.network:
            if portgroup_morid == portgroup._moId:
                continue
            config_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
            name = portgroup.name +'='
            #portgroup.Rename_Task(name)
        
        uuid_sh_str = "grep 'data.uuid' /Users/yanz3/runtime.properties  | awk -F '=' '{print $2}'"
        uuid = subprocess.Popen(uuid_sh_str, shell=True, stdout=subprocess.PIPE)
        print uuid.communicate() 
        
        #portgroup_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                                #[vim.DistributedVirtualSwitch],
                                                                #[vim.ClusterComputeResource],
        #                                                        [vim.dvs.DistributedVirtualPortgroup],
        #                                                        True)
        #dc_pg_view = portgroup_view.view
        #portgroup_view.Destroy()
        #portgroup_key = None
        #for portgroup in dc_pg_view:
            #dvps=portgroup.environmentBrowser.QueryConfigTarget(host).distributedVirtualPortgroup
            #dvports=portgroup.FetchDVPorts(vim.dvs.PortCriteria(uplinkPort=True))
            #print("{}\t{}\t".format("Portgroup Name:    ", portgroup.name))
            #print("{}\t{}\t\n".format("Portgroup Key:    ", portgroup.key))
            #print("{}\t{}\t\n".format("Portgroup Key:    ", portgroup.config))
            #if portgroup.name.startswith("Management Network") :
                #portgroup_key = portgroup.key
            #if portgroup_morid == portgroup._moId:
            #    continue
            #config_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
            #config_spec.name = portgroup.name +'='
            #portgroup.ReconfigureDVPortgroup(config_spec)
            #print portgroup.key


    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

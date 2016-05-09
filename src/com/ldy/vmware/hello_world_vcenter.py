#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2013 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program to authenticate and print
a friendly encouragement to joining the community!
"""

import atexit
import argparse
import getpass

# Opt out with PEP 476
#import ssl
#import requests
#requests.packages.urllib3.disable_warnings()
#if hasattr(ssl, '_create_unverified_context'):
#    ssl._create_default_https_context = ssl._create_unverified_context  # pylint: disable=W0212

from pyVim import connect
from pyVmomi import vmodl



def get_args():
    """Get command line args from the user.
    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

    # because -h is reserved for 'help' we use -s for service
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    # because we want -p for password, we use -o for port
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args


def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

    #args = get_args()

    try:
        import ssl
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
                
        service_instance = connect.SmartConnect(host="10.62.92.50",
                                                user="root",
                                                pwd="Testesx123!",
                                                port=int("443"),
                                                sslContext=context)

        atexit.register(connect.Disconnect, service_instance)

        print ("\nHello World!\n")
        print ("If you got here, you authenticted into vCenter.")
        print ("The server is {}!").format("10.62.81.28")
        # NOTE (hartsock): only a successfully authenticated session has a
        # session key aka session id.
        session_id = service_instance.content.sessionManager.currentSession.key
        print ("current session id: {}").format(session_id)
        print ("Well done!")
        print ("\n")
        print ("Download, learn and contribute back:")
        print ("https://github.com/vmware/pyvmomi-community-samples")
        print ("\n\n")

    except vmodl.MethodFault as error:
        print ("Caught vmodl fault : ") + error.msg
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

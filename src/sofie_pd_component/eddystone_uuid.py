"""
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed
# with this work for additional information regarding copyright
# ownership.  The ASF licenses this file to you under the Apache
# License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License.  You may obtain a copy of the
# License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

"""

"""
Eddystone UUID

Eddystone URL is used to transmit a web address i.e Uniform Resource Locator (URL) over Bluetooth.
Eddystone has a two part identifier that consists of a 10 byte namespace identifier and a 6 byte instance identifier. 
This is python script to run Eddystone URL over local BLE device. 
            
"""

import re
import os
import signal
import subprocess
import sys
import time
import argparse
from pprint import pprint

if sys.version_info > (3, 0):
    DEVNULL = subprocess.DEVNULL
else:
    DEVNULL = open(os.devnull, "wb")


def add_space(string, length):
    """This method is used to format Unique ID into the Eddystone format."""
    return " ".join(string[i : i + length] for i in range(0, len(string), length))

def change_type(vari):
    if not isinstance(vari, str):
        vari = vari.hex()
    return vari


def startUuidAdvertise(INTERFACE, TXPOWER, NAMESPACE, INSTANCEID):
    """
    This method is used to start the advertisement of eddystone url over bluetooth.
    
    :param string NAMESPACE: 10 byte unique ID to signify your company or organization
    :param string INSTANCEID: 6 byte instance ID to identify the device.
    
    """
    
    NAMESPACE = add_space(change_type(NAMESPACE), 2)
    INSTANCEID = add_space(change_type(INSTANCEID), 2)
    print("Advertising: " + NAMESPACE + INSTANCEID)
    INTERFACE = change_type(INTERFACE)
    TXPOWER = change_type(TXPOWER)
    
    subprocess.call("sudo hciconfig " + INTERFACE + " up", shell=True, stdout=DEVNULL)
    init = (
        "sudo hcitool -i " + INTERFACE + " cmd 0x08 0x0008 1E 02 01 06 03 03 AA FE 15 16 AA FE 00 " + TXPOWER
    )
    finalCommand = init + " " + NAMESPACE + " " + INSTANCEID
    # Stop advertising
    subprocess.call(
        "sudo hcitool -i "+ INTERFACE + " cmd 0x08 0x000a 00", shell=True, stdout=DEVNULL
    )
    # Set advertising type
    subprocess.call("sudo hciconfig -a " + INTERFACE + " leadv 3", shell=True, stdout=DEVNULL)
    # Set uuid
    subprocess.call(finalCommand, shell=True, stdout=DEVNULL)
    # Resume advertising
    subprocess.call(
        "sudo hcitool -i " + INTERFACE +" cmd 0x08 0x000a 01", shell=True, stdout=DEVNULL
    )


def stopUuidAdvertise(INTERFACE):
    """ This method gets called to stop the advertisement. """
    print("Stopping advertising")
    subprocess.call(
        "sudo hcitool -i "+ INTERFACE + " cmd 0x08 0x000a 00", shell=True, stdout=DEVNULL
    )

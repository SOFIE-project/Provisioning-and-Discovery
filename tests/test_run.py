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

from sys import argv
import subprocess
import time
import sys
import json
import requests

sys.path.append("./src")

from sofie_pd_component.gatt_application import BLE
from sofie_pd_component.eddystone_url import startUrlAdvertise, stopUrlAdvertise
from sofie_pd_component.eddystone_uuid import startUuidAdvertise, stopUuidAdvertise
from sofie_pd_component.dns import run

if sys.version_info > (3, 0):
    DEVNULL = subprocess.DEVNULL
else:
    DEVNULL = open(os.devnull, "wb")

URL = "//google.com"
NAME = "TEST"
UUID = "00000000000000000000000000000000" 


def restart_bluetooth():
    """This method is used to reset Bluetooth interface for clearing any previous settings. """
    print("Restarting Bluetooth")
    subprocess.call("sudo hciconfig -a hci0 down", shell=True, stdout=DEVNULL)
    time.sleep(2)
    subprocess.call("sudo hciconfig -a hci0 up", shell=True, stdout=DEVNULL)


def start_uuid_advertise():
    print("Test - Start UUID Advertising")
    restart_bluetooth()
    try:
        if len(UUID) == 32:
            NAMESPACE = UUID[:10]
            INSTANCEID = UUID[10:]
            subprocess.call(["sudo", "-v"])
            startUuidAdvertise('hci0', bytes.fromhex('E7'), bytes.fromhex(NAMESPACE), bytes.fromhex(INSTANCEID))
    except:
        print("Test Failed")

def stop_uuid_advertise():
    print("Test - Stop UUID Advertising")
    try:
        stopUuidAdvertise()
    except:
        print("Test Failed")
    
def start_url_advertise():
    print("Test - Start URL Advertising")
    restart_bluetooth()
    try:
        startUrlAdvertise("http:" + URL)
    except:
        print("Test Failed")

def stop_url_advertise():
    print("Test - Stop URL Advertising")
    try:
        stopUrlAdvertise()
    except:
        print("Test Failed")

def server_startup():
    print("Test - Starting DNS-SD")
    try:
        run()
    except:
        print("Test Failed")
    

if __name__ == '__main__':
    print("##### Starting Tests ######")
    start_uuid_advertise()
    stop_uuid_advertise()
    start_url_advertise()
    stop_url_advertise()
    print("##### Ending Tests #####")
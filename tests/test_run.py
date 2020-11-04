from sys import argv
import subprocess
import time
import sys
import json
import requests

sys.path.append("./src")

from gatt_application import BLE
import eddystone_url
import eddystone_uuid
from python_app.controller import app

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
    if len(UUID) == 32:
        NAMESPACE = UUID[:10]
        INSTANCEID = UUID[10:]
        subprocess.call(["sudo", "-v"])
        eddystone_uuid.startAdvertise(NAMESPACE, INSTANCEID)

def stop_uuid_advertise():
    print("Test - Stop UUID Advertising")
    eddystone_uuid.stopAdvertise()
    
def start_url_advertise():
    print("Test - Start URL Advertising")
    restart_bluetooth()
    eddystone_url.startAdvertise("http:" + URL)

def stop_url_advertise():
    print("Test - Stop URL Advertising")
    eddystone_url.stopAdvertise()

def server_startup():
    app.run(debug=True)
    url= "http://" + app.config['HOST'] + ':' + app.config['PORT']
    print (url)
    #requests-get
    
    

if __name__ == '__main__':
    start_uuid_advertise()
    stop_uuid_advertise()
    start_url_advertise()
    stop_url_advertise()
    server_startup()
from sys import argv
import subprocess
import time
import sys
import json

sys.path.append("./src")

from gatt_application import BLE
import eddystone_url
import eddystone_uuid
from python_app import run

if sys.version_info > (3, 0):
    DEVNULL = subprocess.DEVNULL
else:
    DEVNULL = open(os.devnull, "wb")

URL = "//google.com"
NAME = "TEST"
DEFAULT_SERVICEUUID = "180A"


def restart_bluetooth():
    """This method is used to reset Bluetooth interface for clearing any previous settings. """
    print("Restarting Bluetooth ......")
    subprocess.call("sudo hciconfig -a hci0 down", shell=True, stdout=DEVNULL)
    time.sleep(2)
    subprocess.call("sudo hciconfig -a hci0 up", shell=True, stdout=DEVNULL)



def start_uuid_advertise():
	restart_bluetooth()
	UUID = BLE(NAME, DEFAULT_SERVICEUUID, URL)
	restart_bluetooth()
	if len(UUID) == 32:
		NAMESPACE = UUID[:10]
		INSTANCEID = UUID[10:]
		subprocess.call(["sudo", "-v"])
		eddystone_uuid.startAdvertise(NAMESPACE, INSTANCEID)

def stop_uuid_advertise():
	restart_bluetooth()
	eddystone_uuid.stopAdvertise()

if __name__ == '__main__':
    start_uuid_advertise()
    stop_uuid_advertise()
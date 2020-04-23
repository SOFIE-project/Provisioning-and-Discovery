"""
Command Line Interface

This is the custom command line interface to work with Discovery and Provisioning component.

After starting the interface, there are limited options to perform

'dns': Start the DNS-SD
'ble': Start the BLE with custom advertising and UART service.
'eddystone' : Start or Stop Eddystone URL
'help': To get the commands
'exit: Exit the interface

"""

from enum import Enum, auto
from sys import argv
import subprocess
import time
import sys
import json

# FOR BLE ADVERTISEMENT
from gatt_application import BLE

# FOR EDDYSTONE URL
import eddystone_url

# FOR EDDYSTONE UUID
import eddystone_uuid

# FOR DNS-SD
from python_app import run


# VARIABLES FOR BLE
URL = "//goo.gl/SkcDTN"
NAME = "DPP"
DEFAULT_SERVICEUUID = "180A"


if sys.version_info > (3, 0):
    DEVNULL = subprocess.DEVNULL
else:
    DEVNULL = open(os.devnull, "wb")

# CLI app to test Discovery & Provisioning component

HELP_CMDS = """Commands:
    - dns
    - ble
    - eddystone
    - help
    - exit"""


def print_help():
    """Print the CLI commands"""
    # Print the CLI commands
    print(f"{HELP_CMDS}")
    print()


def restart_bluetooth():
    """This method is used to reset Bluetooth interface for clearing any previous settings. """
    # Restart Bluetooth interface for clearing settings
    print("Restarting Bluetooth ......")
    subprocess.call("sudo hciconfig -a hci0 down", shell=True, stdout=DEVNULL)
    time.sleep(2)
    subprocess.call("sudo hciconfig -a hci0 up", shell=True, stdout=DEVNULL)


def main():

    print("Starting CLI")

    # Input
    class Cli_input(Enum):
        CONFIG = auto()
        INPUT_LEN = auto()

    while True:

        cmd = input("Type a command)> ")

        keywords = cmd.split()
        cmd = keywords[0]

        if cmd == "dns":
            run()

        elif cmd == "ble":
            restart_bluetooth()
            UUID = BLE(NAME, DEFAULT_SERVICEUUID, URL)
            restart_bluetooth()
            if len(UUID) == 32:
                NAMESPACE = UUID[:10]
                INSTANCEID = UUID[10:]
                subprocess.call(["sudo", "-v"])
                eddystone_uuid.startAdvertise(NAMESPACE, INSTANCEID)

        elif cmd == "eddystone":
            subprocess.call(["sudo", "-v"])
            if len(keywords) is not 2:
                print("Needs 1 parameter atleast")
                continue
            elif keywords[1] == "start":
                eddystone_url.startAdvertise("http:" + URL)
            elif keywords[1] == "stop":
                eddystone_url.stopAdvertise()

        elif cmd == "help":
            print_help()

        elif cmd == "exit":
            print("Quitting CLI")
            break

        else:
            print("Invalid command")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Quitting CLI after interruption from keyboard")

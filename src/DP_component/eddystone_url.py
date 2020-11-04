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
Eddystone URL

Eddystone URL is used to transmit a web address i.e Uniform Resource Locator (URL) over Bluetooth.
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

# List of Valid Schemes
schemes = [
    "http://www.",
    "https://www.",
    "http://",
    "https://",
]
# List of Valid Extentions
extensions = [
    ".com/",
    ".org/",
    ".net/",
    ".com",
    ".org",
    ".net",
]


def encodeurl(url):
    """ This method is used to convert the web address into a URL format and to check its validity for errors."""
    i = 0
    data = []
    for s in range(len(schemes)):
        scheme = schemes[s]
        if url.startswith(scheme):
            data.append(s)
            i += len(scheme)
            break
    else:
        raise Exception("Invalid url scheme")

    while i < len(url):
        if url[i] == ".":
            for e in range(len(extensions)):
                expansion = extensions[e]
                if url.startswith(expansion, i):
                    data.append(e)
                    i += len(expansion)
                    break
            else:
                data.append(0x2E)
                i += 1
        else:
            data.append(ord(url[i]))
            i += 1
    return data


def encodeMessage(url):
    """ This method is called to encode the message into Eddystone URL format."""
    encodedurl = encodeurl(url)
    encodedurlLength = len(encodedurl)

    if encodedurlLength > 18:
        raise Exception("Encoded url too long (max 18 bytes)")
    # Message format for Eddystone
    message = [
        0x02,
        0x01,
        0x1A,
        0x03,
        0x03,
        0xAA,
        0xFE,
        5 + len(encodedurl),
        0x16,
        0xAA,
        0xFE,
        0x10,
        0xED,
    ]

    message += encodedurl

    return message


def startAdvertise(url):
    """
    This method is used to start the advertisement of eddystone url over bluetooth.
    
    :param array{string} schemes: List of the valid schemes used to form a URL.
    :param array{string} extensions: List of the valid web extentions used to form a URL.
    :param string url: Uniform Resource Locator to be advertised over bluetooth.
    """
    print("Advertising: " + url)
    message = encodeMessage(url)
    # Prepend the length of the whole message
    message.insert(0, len(message))
    while len(message) < 32:
        message.append(0x00)
    # Make a list of hex strings from the list of numbers
    message = map(lambda x: "%02x" % x, message)
    # Concatenate all the hex strings, separated by spaces
    message = " ".join(message)
    subprocess.call("sudo hciconfig hci0 up", shell=True, stdout=DEVNULL)
    # Stop advertising
    subprocess.call(
        "sudo hcitool -i hci0 cmd 0x08 0x000a 00", shell=True, stdout=DEVNULL
    )
    # Set message
    subprocess.call(
        "sudo hcitool -i hci0 cmd 0x08 0x0008 " + message, shell=True, stdout=DEVNULL
    )
    # Resume advertising
    subprocess.call(
        "sudo hcitool -i hci0 cmd 0x08 0x000a 01", shell=True, stdout=DEVNULL
    )


def stopAdvertise():
    """ This method gets called to stop the advertisement. """
    print("Stopping advertising")
    subprocess.call(
        "sudo hcitool -i hci0 cmd 0x08 0x000a 00", shell=True, stdout=DEVNULL
    )

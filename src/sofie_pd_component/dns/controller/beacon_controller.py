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

from flask import jsonify, request
from bson.objectid import ObjectId
import json
from sofie_pd_component.dns.model import DB
from . import bad_request_response, app

import os
import subprocess

database = DB()


def add_space(string, length):
    return " ".join(string[i : i + length] for i in range(0, len(string), length))


"""
    Add a new beacon
"""


@app.route("/api/beacon", methods=["POST"])
def add_beacon():
    data = request.get_json()
    if data.get("mac", None) is not None:
        response = database.add_beacon(data)
    if not response:
        return bad_request_response(message="Failed! Beacon was not created")
    return jsonify({"code": 200, "message": "Success", "data": response})


"""
    Get a beacon using mac
"""


@app.route("/api/beacon/<beacon_id>", methods=["GET"])
def get_beacon(beacon_id):
    response = database.get_beacon(beacon_id)
    if not response:
        return bad_request_response(message="Failed! Beacon not found")
    return jsonify({"code": 200, "message": "Success", "data": response["Item"]})


"""
    #Check the status of bluetoooth
"""


@app.route("/api/status", methods=["GET"])
def check_status():
    interface = subprocess.Popen(
        ["sudo hciconfig -a hci0"], stdout=subprocess.PIPE, shell=True
    )
    (int, err) = interface.communicate()
    print (int.split())
    if b"UP" in int.split():
        return jsonify({"code": 200, "message": "Success", "data": "RUNNING"})
    elif b"DOWN" in int.split():
        return jsonify({"code": 200, "message": "Success", "data": "DOWN"})
    else:
        return bad_request_response(message="Failed! Beacon not found")


@app.route("/api/switch", methods=["GET"])
def switch():
    interface = subprocess.Popen(
        ["sudo hciconfig -a hci0"], stdout=subprocess.PIPE, shell=True
    )
    (int, err) = interface.communicate()
    if b"UP" in int.split():
        interface = subprocess.Popen(
            ["sudo hciconfig -a hci0 down"], stdout=subprocess.PIPE, shell=True
        )
        return jsonify({"code": 200, "message": "Success"})
    elif b"DOWN" in int.split():
        interface = subprocess.Popen(
            ["sudo hciconfig -a hci0 up"], stdout=subprocess.PIPE, shell=True
        )
        (int, err) = interface.communicate()
        interface = subprocess.Popen(
            ["sudo hciconfig -a hci0 leadv 3"], stdout=subprocess.PIPE, shell=True
        )
        (int, err) = interface.communicate()
        return jsonify({"code": 200, "message": "Success"})


@app.route("/api/eddystone", methods=["POST"])
def beacon_switch():
    data = request.get_json()
    namespace = data.get("NAMESPACE", None)
    instanceID = data.get("instanceID", None)
    if (len(namespace)==20 and namespace.isalnum()) and len(instanceID)== 12:
        init = (
            "sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 06 03 03 AA FE 15 16 AA FE 00 E7"
        )
        command = init + " " + add_space(namespace, 2) + " " + add_space(instanceID,2)
        interface = subprocess.Popen(
            ["sudo hciconfig -a hci0 leadv 3"], stdout=subprocess.PIPE, shell=False
        )
        interface = subprocess.Popen([command], stdout=subprocess.PIPE, shell=False)
        (int, err) = interface.communicate()
        return jsonify({"code": 200, "message": "Success", "data": int})
    else:
        return bad_request_response(message="Failed! Check namespace and instanceID")
        


@app.route("/api/semantic", methods=["GET"])
def get_semantic():
    filename = os.path.join(app.static_folder, "semantic.json")
    with open(filename) as blog_file:
        data = json.load(blog_file)
    return jsonify({"code": 200, "message": "Success", "data": data})

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

import os
import json
import datetime
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId

from DP_component.dns.model import DB

app = Flask(__name__)
# app.decimal_encoder = DecimalEncoder
# app.url_map.converters['ObjectId'] = ObjectIDConverter

CORS(app)


def create_error_response(status_code, code=0, message=None):
    response = jsonify(code=code, message=message, data=None)
    response.status_code = status_code
    return response


def bad_request_response(message=None):
    return create_error_response(400, message=message)


@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, message="This resource url does not exist")


@app.errorhandler(400)
def resource_not_found(error):
    return create_error_response(400, message="Invalid or missing parameters")


@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(
        500, message="The system has failed. Please, contact the administrator"
    )


@app.route("/")
def hello_world():
    return jsonify({"message": "Hello World!"})


import DP_component.dns.controller.beacon_controller

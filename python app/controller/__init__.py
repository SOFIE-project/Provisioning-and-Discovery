import os
import json
import datetime
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId

from model import DB

app = Flask(__name__)
#app.decimal_encoder = DecimalEncoder
#app.url_map.converters['ObjectId'] = ObjectIDConverter

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
    return create_error_response(400, message='Invalid or missing parameters')


@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, message="The system has failed. Please, contact the administrator")

@app.route('/')
def hello_world():
    return jsonify({"message": "Hello World!"})

import controller.beacon_controller 
#import controllers.hunt_controller
#import controllers.player_controller
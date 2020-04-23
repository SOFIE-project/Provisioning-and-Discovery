import click
import datetime
import json
from bson.objectid import ObjectId
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

from python_app.controller import app

# if __name__ == '__main__':
# Run the app
def run():
    app.run(host="0.0.0.0")

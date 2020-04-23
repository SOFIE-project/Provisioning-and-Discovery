import json
from decimal import Decimal
import os
import time
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError


class DB(object):
    def __init__(self):
        super(DB, self).__init__()
        self.dynamodb = boto3.resource("dynamodb", region_name="us-west-1")

    def add_beacon(self, data):
        table = self.dynamodb.Table("iotbeacon")
        beacon = {
            "ID": str(data.get("mac", None)),  # mac address
            "UUID": data.get("UUID", None),
            "major": data.get("major", None),
            "minor": data.get("minor", None),
            "gps": data.get("gps", None),
            "created_at": str(datetime.utcnow()),
        }
        try:
            response = table.put_item(Item=beacon, ReturnValues="ALL_OLD")
            return response
        except ClientError as e:
            print("Unexpected error: %s" % e)

    def get_beacon(self, Id):
        table = self.dynamodb.Table("iotbeacon")
        try:
            response = table.get_item(Key={"ID": Id})
            return response
        except ClientError as e:
            print("Unexpected error: %s" % e)

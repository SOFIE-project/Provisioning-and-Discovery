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

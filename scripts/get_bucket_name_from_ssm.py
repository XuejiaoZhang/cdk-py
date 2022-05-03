#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Get S3 bucket name for testmon database file from Parameter Store.
"""

import os
import boto3

ssm_client = boto3.client("ssm")

if __name__ == "__main__":
    response = ssm_client.get_parameter(
        Name="smart-testing-testmondata-bucket-name",
    )
    bucket_name = response.get("Parameter", {}).get("Value", "")
    print(bucket_name)

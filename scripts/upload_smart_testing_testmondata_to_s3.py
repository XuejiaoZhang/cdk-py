#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Upload testmon database file to S3 bucket after running smart testing with testmon.
"""
import os
import boto3

s3 = boto3.resource("s3")
s3_bucket = os.getenv("BUCKET_NAME")


if __name__ == "__main__":
    s3.Object(s3_bucket, ".testmondata").upload_file(".testmondata")

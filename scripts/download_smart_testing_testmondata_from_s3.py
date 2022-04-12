#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Download testmon database file from S3 bucket before running smart testing with testmon.
"""

import os
import boto3
import logging

s3 = boto3.resource("s3")
s3_bucket = os.getenv("BUCKET_NAME")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    try:
        s3.meta.client.download_file(s3_bucket, ".testmondata", ".testmondata")
    # s3.meta.client.download_file(s3_bucket, "New Recording 3.m4a", "New Recording 3.m4a")
    except boto3.exceptions.botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.info(f"The object: .testmondata does not exist in {s3_bucket}")

        else:
            logger.info(
                f"Error downloading object: .testmondata from {s3_bucket}: {str(e)}"
            )
            raise

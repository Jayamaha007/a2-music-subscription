"""
Shared S3 helpers used by Lambda handlers that need artist images.
Generates pre-signed URLs for objects stored in the images S3 bucket.
"""
import boto3

s3 = boto3.client("s3")

# TODO: implement generate_presigned_url(bucket, key, expiry=3600)

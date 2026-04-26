"""
Downloads artist images from each song's `image_url` field and uploads them to S3.
Objects are stored under the key: images/<artist>/<filename>.
Access is via pre-signed URLs — no public bucket policy is set.
"""
import boto3
import requests

# TODO: implement image download + S3 upload


import os
import boto3

s3     = boto3.client('s3')
BUCKET = os.environ.get('S3_BUCKET_NAME', '')

def generate_presigned_url(image_key, expiry=3600):
    """Return a pre-signed GET URL for the given S3 object key."""
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET, 'Key': image_key},
        ExpiresIn=expiry
    )

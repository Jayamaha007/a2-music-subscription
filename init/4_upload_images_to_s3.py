"""
Downloads each unique artist image from its img_url in 2026a2_songs.json
and uploads it to the S3 bucket used by the application.

S3 key format: <artist_lowercase>.jpg   e.g. taylor_swift.jpg  (matches UploadArtistImagesToS3.java)
Access is via pre-signed URLs only — no public bucket policy is set.

Run after 3_load_songs.py:
  python3 4_upload_images_to_s3.py

Requirements:
  pip install requests boto3
"""
import os
import boto3
import json
import re
import requests
from botocore.exceptions import ClientError

REGION      = os.environ.get("AWS_REGION", "us-east-1")
BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "")
JSON_FILE   = os.path.join(os.path.dirname(__file__), "2026a2_songs.json")

s3 = boto3.client("s3", region_name=REGION)


def ensure_bucket():
    """Create the S3 bucket if it doesn't already exist."""
    try:
        if REGION == "us-east-1":
            s3.create_bucket(Bucket=BUCKET_NAME)
        else:
            s3.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": REGION},
            )
        print(f"  Bucket '{BUCKET_NAME}' created.")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
            print(f"  Bucket '{BUCKET_NAME}' already exists — skipping creation.")
        else:
            raise


def upload_images():
    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    # Deduplicate by artist — key format matches UploadArtistImagesToS3.java:
    # re.sub(r'[^a-zA-Z0-9]', '_', artist).lower() + ".jpg"
    seen = {}
    for song in data["songs"]:
        artist  = song.get("artist", "")
        img_url = song.get("img_url", "")
        if artist and img_url:
            s3_key = re.sub(r'[^a-zA-Z0-9]', '_', artist).lower() + ".jpg"
            seen[s3_key] = img_url

    print(f"Uploading {len(seen)} unique artist images to s3://{BUCKET_NAME}/")

    success = 0
    failed  = 0

    for s3_key, url in seen.items():
        filename = s3_key
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()

            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=filename,
                Body=resp.content,
                ContentType="image/jpeg",
            )
            print(f"  Uploaded: {filename}")
            success += 1
        except Exception as e:
            print(f"  FAILED: {filename} — {e}")
            failed += 1

    print(f"\nDone. Uploaded: {success}, Failed: {failed}")


if __name__ == "__main__":
    print(f"Setting up S3 bucket '{BUCKET_NAME}'...")
    ensure_bucket()
    upload_images()

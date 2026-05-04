"""
Loads all songs from 2026a2_songs.json into the DynamoDB Music table.

Field mapping from JSON → DynamoDB:
  img_url  → image_key  (S3 key: lowercase artist name, special chars → _, e.g. taylor_swift.jpg)
  title    → title      (also used in composite SK title_year)
  artist   → artist     (PK)
  year     → year       (Number — matches Java MusicCreateTable schema)
  album    → album

Composite sort key:
  title_year = f"{title}#{year}" — guarantees uniqueness for the 4 duplicate artist+title pairs

Image key format matches UploadArtistImagesToS3.java:
  re.sub(r'[^a-zA-Z0-9]', '_', artist).lower() + '.jpg'

Run after 2_create_music_table.py:
  python3 3_load_songs.py
"""
import os
import boto3
import json
import re
from decimal import Decimal

REGION     = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMODB_MUSIC_TABLE", "Music")
JSON_FILE  = os.path.join(os.path.dirname(__file__), "2026a2_songs.json")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table    = dynamodb.Table(TABLE_NAME)


def image_key_from_artist(artist: str) -> str:
    """Build the S3 key from artist name — matches UploadArtistImagesToS3.java logic."""
    return re.sub(r'[^a-zA-Z0-9]', '_', artist).lower() + ".jpg"


def load_songs():
    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    songs = data["songs"]
    print(f"Loading {len(songs)} songs into '{TABLE_NAME}'...")

    success = 0

    with table.batch_writer() as batch:
        for song in songs:
            title   = song["title"]
            artist  = song["artist"]
            year    = int(song["year"])          # Number — matches Java schema
            album   = song.get("album", "")
            img_url = song.get("img_url", "")
            image_key = image_key_from_artist(artist)

            item = {
                "artist":     artist,
                "title_year": f"{title}#{year}",  # composite SK — avoids duplicates
                "title":      title,
                "year":       year,               # stored as Number
                "album":      album,
                "image_key":  image_key,          # S3 key — used to generate pre-signed URLs
                "img_url":    img_url,            # original URL kept for reference
            }

            batch.put_item(Item=item)
            success += 1

    print(f"  Loaded: {success} songs")
    print("Done.")


if __name__ == "__main__":
    load_songs()

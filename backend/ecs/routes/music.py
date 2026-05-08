import os
import boto3
import re
from boto3.dynamodb.conditions import Key, Attr
from flask import Blueprint, request, jsonify

music_bp = Blueprint("music", __name__)

_region  = os.environ.get("AWS_REGION", "us-east-1")
dynamodb = boto3.resource("dynamodb", region_name=_region)
table    = dynamodb.Table(os.environ.get("DYNAMODB_MUSIC_TABLE", "Music"))

s3     = boto3.client("s3", region_name=_region)
BUCKET = os.environ.get("S3_BUCKET_NAME", "")


def get_image_url(image_key):
    if not image_key:
        return ""
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": image_key},
            ExpiresIn=3600,
        )
    except Exception:
        return ""


def format_items(items):
    result = []
    for item in items:
        result.append({
            "title":     item.get("title", ""),
            "artist":    item.get("artist", ""),
            "year":      str(item.get("year", "")),
            "album":     item.get("album", ""),
            "image_url": get_image_url(item.get("image_key", "")),
            "image_key": item.get("image_key", ""),
        })
    return result


@music_bp.route("/music", methods=["GET"])
def query_music():
    artist = request.args.get("artist", "").strip()
    title  = request.args.get("title",  "").strip()
    album  = request.args.get("album",  "").strip()
    year   = request.args.get("year",   "").strip()

    try:
        # LSI query: artist + year
        if artist and year:
            result = table.query(
                IndexName="year-index",
                KeyConditionExpression=Key("artist").eq(artist) & Key("year").eq(int(year))
            )
            items = result.get("Items", [])
            if title: items = [i for i in items if title.lower() in i.get("title", "").lower()]
            if album: items = [i for i in items if album.lower() in i.get("album", "").lower()]

        # GSI query: title
        elif title:
            result = table.query(
                IndexName="title-index",
                KeyConditionExpression=Key("title").eq(title)
            )
            items = result.get("Items", [])
            if artist: items = [i for i in items if artist.lower() in i.get("artist", "").lower()]
            if album:  items = [i for i in items if album.lower()  in i.get("album",  "").lower()]
            if year:   items = [i for i in items if str(i.get("year", "")) == year]

        # Table PK query: artist only
        elif artist:
            result = table.query(
                KeyConditionExpression=Key("artist").eq(artist)
            )
            items = result.get("Items", [])
            if album: items = [i for i in items if album.lower() in i.get("album", "").lower()]
            if year:  items = [i for i in items if str(i.get("year", "")) == year]

        # Scan fallback
        else:
            filter_parts = []
            if album: filter_parts.append(Attr("album").contains(album))
            if year:  filter_parts.append(Attr("year").eq(int(year)))

            if filter_parts:
                fe = filter_parts[0]
                for part in filter_parts[1:]:
                    fe = fe & part
                result = table.scan(FilterExpression=fe)
            else:
                result = table.scan()

            items = result.get("Items", [])

        return jsonify({"songs": format_items(items)}), 200

    except Exception as e:
        print(f"[music] error: {e}")
        return jsonify({"songs": [], "message": "Internal server error."}), 500

"""
Subscription routes for the EC2 backend.
GET    /subscriptions — fetch all subscriptions for a user.
POST   /subscriptions — add a subscription.
DELETE /subscriptions — remove a subscription.

Subscriptions table structure:
  PK: email   (String)
  SK: song_id (String) — "artist#title"
"""
import os
import boto3
from boto3.dynamodb.conditions import Key
from flask import Blueprint, request, jsonify

subscriptions_bp = Blueprint("subscriptions", __name__)

_region  = os.environ.get("AWS_REGION", "us-east-1")
dynamodb = boto3.resource("dynamodb", region_name=_region)
table    = dynamodb.Table(os.environ.get("DYNAMODB_SUBSCRIPTIONS_TABLE", "Subscriptions"))

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


@subscriptions_bp.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    email = request.args.get("email", "").strip()
    if not email:
        return jsonify({"subscriptions": [], "message": "email is required."}), 400

    try:
        result = table.query(KeyConditionExpression=Key("email").eq(email))
        items  = result.get("Items", [])

        subscriptions = [{
            "title":     item.get("title", ""),
            "artist":    item.get("artist", ""),
            "year":      str(item.get("year", "")),
            "album":     item.get("album", ""),
            "image_url": get_image_url(item.get("image_key", "")),
        } for item in items]

        return jsonify({"subscriptions": subscriptions}), 200

    except Exception as e:
        print(f"[subscriptions GET] error: {e}")
        return jsonify({"subscriptions": [], "message": "Internal server error."}), 500


@subscriptions_bp.route("/subscriptions", methods=["POST"])
def add_subscription():
    body   = request.get_json(force=True) or {}
    email  = body.get("email",  "").strip()
    artist = body.get("artist", "").strip()
    title  = body.get("title",  "").strip()

    if not email or not artist or not title:
        return jsonify({"success": False, "message": "email, artist and title are required."}), 400

    try:
        table.put_item(Item={
            "email":     email,
            "song_id":   f"{artist}#{title}",
            "artist":    artist,
            "title":     title,
            "year":      str(body.get("year", "")),
            "album":     body.get("album", ""),
            "image_key": body.get("image_key", ""),
        })
        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"[subscriptions POST] error: {e}")
        return jsonify({"success": False, "message": "Internal server error."}), 500


@subscriptions_bp.route("/subscriptions", methods=["DELETE"])
def remove_subscription():
    body   = request.get_json(force=True) or {}
    email  = body.get("email",  "").strip()
    artist = body.get("artist", "").strip()
    title  = body.get("title",  "").strip()

    if not email or not artist or not title:
        return jsonify({"success": False, "message": "email, artist and title are required."}), 400

    try:
        table.delete_item(Key={
            "email":   email,
            "song_id": f"{artist}#{title}",
        })
        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"[subscriptions DELETE] error: {e}")
        return jsonify({"success": False, "message": "Internal server error."}), 500

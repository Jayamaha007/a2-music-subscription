"""
Authentication routes for the EC2 backend.
POST /login    — validate email + password against the LoginTable.
POST /register — check uniqueness, write new user to the LoginTable.
"""
import os
import boto3
from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__)

dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
table    = dynamodb.Table(os.environ.get("DYNAMODB_LOGIN_TABLE", "LoginTable"))


@auth_bp.route("/login", methods=["POST"])
def login():
    body     = request.get_json(force=True) or {}
    email    = body.get("email", "").strip()
    password = body.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    result = table.get_item(Key={"email": email})

    if "Item" in result and result["Item"]["password"] == password:
        return jsonify({"success": True, "user_name": result["Item"]["user_name"]}), 200
    else:
        return jsonify({"success": False, "message": "Email or password is incorrect."}), 401


@auth_bp.route("/register", methods=["POST"])
def register():
    body      = request.get_json(force=True) or {}
    email     = body.get("email", "").strip()
    user_name = body.get("user_name", "").strip()
    password  = body.get("password", "")

    if not email or not user_name or not password:
        return jsonify({"success": False, "message": "Email, username and password are required."}), 400

    existing = table.get_item(Key={"email": email})
    if "Item" in existing:
        return jsonify({"success": False, "message": "Email already registered."}), 409

    table.put_item(Item={"email": email, "user_name": user_name, "password": password})
    return jsonify({"success": True}), 200

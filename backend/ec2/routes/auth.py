"""
Authentication routes for the EC2 backend.
POST /login  — validate email + password against the login table.
POST /register — check uniqueness, then write a new user to the login table.
"""
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

# TODO: implement /login and /register

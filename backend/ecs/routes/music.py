"""
Music query routes for the ECS backend.
GET /music — query or scan the music DynamoDB table by title, artist, year, album (AND logic).
"""
from flask import Blueprint

music_bp = Blueprint("music", __name__)

# TODO: implement /music query endpoint

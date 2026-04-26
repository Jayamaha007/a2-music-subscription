"""
Subscription routes for the ECS backend.
GET    /subscriptions — fetch all subscriptions for a user.
POST   /subscriptions — add a subscription.
DELETE /subscriptions — remove a subscription.
"""
from flask import Blueprint

subscriptions_bp = Blueprint("subscriptions", __name__)

# TODO: implement GET, POST, DELETE /subscriptions

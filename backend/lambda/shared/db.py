"""
Shared DynamoDB boto3 helpers used by all Lambda handlers.
Provides pre-configured table resource objects and common query utilities.
"""
import boto3

dynamodb = boto3.resource("dynamodb")

# TODO: implement helper functions (get_item, put_item, query, scan wrappers)

"""
Lambda handler for GET /music.
Accepts optional query parameters: title, artist, year, album.
Builds a DynamoDB Query or Scan with AND logic across all supplied filters.
"""

def lambda_handler(event, context):
    # TODO: implement music query/scan logic
    pass

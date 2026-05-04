"""
Lambda handler for GET /subscriptions.
Fetches all subscription records for a given user from the Subscriptions table.
Regenerates a pre-signed S3 URL for each subscription's artist image.
Returns { subscriptions: [ { title, artist, year, album, image_url }, ... ] }

Subscriptions table structure:
  PK: email    (String)
  SK: song_id  (String) — "artist#title"

This handler did not exist in the original codebase and was created from scratch.
"""
import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ.get('DYNAMODB_SUBSCRIPTIONS_TABLE', 'Subscriptions'))

s3     = boto3.client('s3')
BUCKET = os.environ.get('S3_BUCKET_NAME', '')

HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,OPTIONS',
}

def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': HEADERS, 'body': ''}

    try:
        params = event.get('queryStringParameters') or {}
        email  = params.get('email', '').strip()

        if not email:
            return response(400, {'subscriptions': [], 'message': 'email query parameter is required.'})

        result = table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        items = result.get('Items', [])

        subscriptions = []
        for item in items:
            image_key = item.get('image_key', '')
            image_url = ''
            if image_key:
                try:
                    image_url = s3.generate_presigned_url(
                        'get_object',
                        Params={'Bucket': BUCKET, 'Key': image_key},
                        ExpiresIn=3600
                    )
                except Exception:
                    image_url = ''

            subscriptions.append({
                'title':     item.get('title', ''),
                'artist':    item.get('artist', ''),
                'year':      str(item.get('year', '')),
                'album':     item.get('album', ''),
                'image_url': image_url,
            })

        return response(200, {'subscriptions': subscriptions})

    except Exception as e:
        print(f'[get_subscriptions] error: {e}')
        return response(500, {'subscriptions': [], 'message': 'Internal server error.'})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers':    HEADERS,
        'body':       json.dumps(body, default=str),
    }

"""
Lambda handler for POST /subscriptions.
Writes a new subscription record to the Subscriptions DynamoDB table.

Subscriptions table structure:
  PK: email    (String)
  SK: song_id  (String) — constructed as "artist#title" for uniqueness

Fixes applied over original subscribe.py:
- Parses request body from API Gateway event['body'] (JSON string)
- Constructs song_id from artist + title (frontend does not send song_id)
- Stores image_key so get_subscriptions can regenerate pre-signed URLs
- Returns { success: true } to match frontend expectations
- Adds CORS headers
"""
import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ.get('DYNAMODB_SUBSCRIPTIONS_TABLE', 'Subscriptions'))

HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
}

def lambda_handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 204, 'headers': HEADERS, 'body': ''}

    try:
        body   = json.loads(event.get('body') or '{}')
        email  = body.get('email', '').strip()
        artist = body.get('artist', '').strip()
        title  = body.get('title',  '').strip()

        if not email or not artist or not title:
            return response(400, {'success': False, 'message': 'email, artist and title are required.'})

        song_id = f"{artist}#{title}"

        table.put_item(Item={
            'email':     email,
            'song_id':   song_id,
            'artist':    artist,
            'title':     title,
            'year':      str(body.get('year', '')),
            'album':     body.get('album', ''),
            'image_key': body.get('image_key', ''),  # S3 key; used to regenerate pre-signed URL
        })

        return response(200, {'success': True})

    except Exception as e:
        print(f'[subscribe] error: {e}')
        return response(500, {'success': False, 'message': 'Internal server error.'})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers':    HEADERS,
        'body':       json.dumps(body),
    }

"""
Lambda handler for GET /music.
Queries or scans the Music DynamoDB table using AND logic across supplied filters.
Returns { songs: [ { title, artist, year, album, image_url, image_key }, ... ] }

Music table structure (from original querymusic.py):
  PK:  artist  (String)
  SK:  title   (String)
  LSI: year-index  — PK=artist, SK=year  (query by artist + year)
  GSI: title-index — PK=title            (query by title alone)

Fixes applied over original querymusic.py:
- Reads filters from API Gateway event['queryStringParameters'] instead of top-level event
- Handles all filter combinations cleanly (not just artist+year or title)
- Returns wrapped { songs: [...] } instead of a bare list
- Adds CORS headers
- Passes image_key back so the subscribe handler can store it
"""
import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ.get('DYNAMODB_MUSIC_TABLE', 'Music'))

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
        artist = params.get('artist', '').strip()
        title  = params.get('title',  '').strip()
        album  = params.get('album',  '').strip()
        year   = params.get('year',   '').strip()

        # ── LSI query: artist + year ──────────────────────────────────────
        if artist and year:
            result = table.query(
                IndexName='year-index',
                KeyConditionExpression=Key('artist').eq(artist) & Key('year').eq(int(year))  # year is Number
            )
            items = result.get('Items', [])

            # Post-filter by title / album if also supplied
            if title: items = [i for i in items if title.lower()  in i.get('title', '').lower()]
            if album: items = [i for i in items if album.lower()  in i.get('album', '').lower()]

        # ── GSI query: title ──────────────────────────────────────────────
        elif title:
            result = table.query(
                IndexName='title-index',
                KeyConditionExpression=Key('title').eq(title)
            )
            items = result.get('Items', [])

            # Post-filter by artist / album / year if also supplied
            if artist: items = [i for i in items if artist.lower() in i.get('artist', '').lower()]
            if album:  items = [i for i in items if album.lower()  in i.get('album',  '').lower()]
            if year:   items = [i for i in items if str(i.get('year', '')) == year]

        # ── artist-only query: table PK ───────────────────────────────────
        elif artist:
            result = table.query(
                KeyConditionExpression=Key('artist').eq(artist)
            )
            items = result.get('Items', [])
            if album: items = [i for i in items if album.lower() in i.get('album', '').lower()]
            if year:  items = [i for i in items if str(i.get('year', '')) == year]

        # ── Fallback: scan with whatever filters we have ──────────────────
        else:
            filter_parts = []
            if album: filter_parts.append(Attr('album').contains(album))
            if year:  filter_parts.append(Attr('year').eq(int(year)))

            if filter_parts:
                fe = filter_parts[0]
                for part in filter_parts[1:]:
                    fe = fe & part
                result = table.scan(FilterExpression=fe)
            else:
                result = table.scan()

            items = result.get('Items', [])

        # ── Attach pre-signed image URL ───────────────────────────────────
        for item in items:
            image_key = item.get('image_key', '')
            if image_key:
                item['image_url'] = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET, 'Key': image_key},
                    ExpiresIn=3600
                )
            else:
                item['image_url'] = ''
            # Convert Decimal year to int for JSON serialisation
            if 'year' in item:
                item['year'] = str(item['year'])

        return response(200, {'songs': items})

    except Exception as e:
        print(f'[query] error: {e}')
        return response(500, {'songs': [], 'message': 'Internal server error.'})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers':    HEADERS,
        'body':       json.dumps(body, default=str),
    }

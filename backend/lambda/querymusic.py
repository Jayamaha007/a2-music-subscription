import boto3
from boto3.dynamodb.conditions import Key, Attr
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Music')

s3 = boto3.client('s3')
BUCKET = 'chathraka-music-images-2026'

def generate_url(key):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET, 'Key': key},
        ExpiresIn=3600
    )

def lambda_handler(event, context):

    artist = event.get('artist')
    title = event.get('title')
    album = event.get('album')
    year = event.get('year')

    # LSI Query
    if artist and year:
        response = table.query(
            IndexName='year-index',
            KeyConditionExpression=Key('artist').eq(artist) & Key('year').eq(int(year))
        )

    # GSI Query
    elif title:
        response = table.query(
            IndexName='title-index',
            KeyConditionExpression=Key('title').eq(title)
        )

    #  Scan
    else:
        response = table.scan(
            FilterExpression=Attr('artist').eq(artist) & Attr('album').eq(album)
        )

    items = response.get('Items', [])

    # attach image URL
    for item in items:
        item['image_url'] = generate_url(item['image_key'])

    return items
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Subscriptions')

def lambda_handler(event, context):

    table.put_item(Item={
        'email': event['email'],
        'song_id': event['song_id'],
        'artist': event['artist'],
        'title': event['title'],
        'year': int(event['year']),
        'album': event['album']
    })

    return {'status': 'subscribed'}
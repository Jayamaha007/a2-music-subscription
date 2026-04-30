import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Subscriptions')

def lambda_handler(event, context):

    table.delete_item(
        Key={
            'email': event['email'],
            'song_id': event['song_id']
        }
    )

    return {'status': 'removed'}
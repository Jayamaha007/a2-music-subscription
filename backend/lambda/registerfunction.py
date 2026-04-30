import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LoginTable')

def lambda_handler(event, context):

    email = event.get('email')

    if 'Item' in table.get_item(Key={'email': email}):
        return {'status': 'error', 'message': 'Email exists'}

    table.put_item(Item={
        'email': email,
        'user_name': event.get('username'),
        'password': event.get('password')
    })

    return {'status': 'success'}
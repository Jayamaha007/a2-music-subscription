import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LoginTable')

def lambda_handler(event, context):

    email = event.get('email')
    password = event.get('password')

    response = table.get_item(Key={'email': email})

    if 'Item' in response and response['Item']['password'] == password:
        return {
            'status': 'success',
            'username': response['Item']['user_name']
        }
    else:
        return {
            'status': 'error',
            'message': 'Invalid credentials'
        }
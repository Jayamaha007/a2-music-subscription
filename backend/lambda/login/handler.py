
import json
import os
import boto3

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table(os.environ.get('DYNAMODB_LOGIN_TABLE', 'LoginTable'))

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
        body     = json.loads(event.get('body') or '{}')
        email    = body.get('email', '').strip()
        password = body.get('password', '')

        if not email or not password:
            return response(400, {'success': False, 'message': 'Email and password are required.'})

        result = table.get_item(Key={'email': email})

        if 'Item' in result and result['Item']['password'] == password:
            return response(200, {
                'success':   True,
                'user_name': result['Item']['user_name']
            })
        else:
            return response(401, {'success': False, 'message': 'Email or password is incorrect.'})

    except Exception as e:
        print(f'[login] error: {e}')
        return response(500, {'success': False, 'message': 'Internal server error.'})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers':    HEADERS,
        'body':       json.dumps(body),
    }

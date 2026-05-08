
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
        body      = json.loads(event.get('body') or '{}')
        email     = body.get('email', '').strip()
        user_name = body.get('user_name', '').strip()
        password  = body.get('password', '')

        if not email or not user_name or not password:
            return response(400, {'success': False, 'message': 'Email, username and password are required.'})

        # Check if email already registered
        existing = table.get_item(Key={'email': email})
        if 'Item' in existing:
            return response(409, {'success': False, 'message': 'Email already registered.'})

        table.put_item(Item={
            'email':     email,
            'user_name': user_name,
            'password':  password,
        })

        return response(200, {'success': True})

    except Exception as e:
        print(f'[register] error: {e}')
        return response(500, {'success': False, 'message': 'Internal server error.'})


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers':    HEADERS,
        'body':       json.dumps(body),
    }

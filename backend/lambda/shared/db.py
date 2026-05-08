
import os
import boto3

dynamodb = boto3.resource('dynamodb')

login_table         = dynamodb.Table(os.environ.get('DYNAMODB_LOGIN_TABLE', 'LoginTable'))
music_table         = dynamodb.Table(os.environ.get('DYNAMODB_MUSIC_TABLE', 'Music'))
subscriptions_table = dynamodb.Table(os.environ.get('DYNAMODB_SUBSCRIPTIONS_TABLE', 'Subscriptions'))

"""
Creates and seeds the DynamoDB LoginTable with 10 user records.
Schema:
  PK: email (String)
  Attributes: user_name (String), password (String)

Run once: python3 1_seed_login_table.py
"""
import os
import boto3
from botocore.exceptions import ClientError

REGION     = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMODB_LOGIN_TABLE", "LoginTable")

# Users loaded from logindata.json (provided with the assignment)
USERS = [
    {"email": "S41414190@student.rmit.edu.au", "user_name": "Chathraka0", "password": "012345"},
    {"email": "S41414191@student.rmit.edu.au", "user_name": "Chathraka1", "password": "123456"},
    {"email": "S41414192@student.rmit.edu.au", "user_name": "Chathraka2", "password": "234567"},
    {"email": "S41414193@student.rmit.edu.au", "user_name": "Chathraka3", "password": "345678"},
    {"email": "S41414194@student.rmit.edu.au", "user_name": "Chathraka4", "password": "456789"},
    {"email": "S41414195@student.rmit.edu.au", "user_name": "Chathraka5", "password": "567890"},
    {"email": "S41414196@student.rmit.edu.au", "user_name": "Chathraka6", "password": "678901"},
    {"email": "S41414197@student.rmit.edu.au", "user_name": "Chathraka7", "password": "789012"},
    {"email": "S41414198@student.rmit.edu.au", "user_name": "Chathraka8", "password": "890123"},
    {"email": "S41414199@student.rmit.edu.au", "user_name": "Chathraka9", "password": "901234"},
]

dynamodb = boto3.client("dynamodb", region_name=REGION)
resource = boto3.resource("dynamodb", region_name=REGION)


def create_table():
    print(f"Creating table '{TABLE_NAME}'...")
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "email", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=TABLE_NAME)
        print(f"  Table '{TABLE_NAME}' created.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"  Table '{TABLE_NAME}' already exists — skipping creation.")
        else:
            raise


def seed_users():
    table = resource.Table(TABLE_NAME)
    print(f"Seeding {len(USERS)} users...")
    for user in USERS:
        table.put_item(Item=user)
        print(f"  Added: {user['email']}")
    print("Done.")


if __name__ == "__main__":
    create_table()
    seed_users()

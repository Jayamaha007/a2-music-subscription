"""
Creates the DynamoDB Music table with the correct key schema, GSI, and LSI.

Key schema (chosen to avoid data loss — see docs/schema_design.md):
  PK:  artist      (String)  — partition key
  SK:  title#year  (String)  — sort key; composite avoids 4 duplicate artist+title pairs

LSI  year-index:
  PK:  artist  (same as table)
  SK:  year    (String)
  Use: query all songs by a specific artist in a given year

GSI  title-index:
  PK:  title   (String)
  SK:  artist  (String)
  Use: query songs by title regardless of artist

Run once: python3 2_create_music_table.py
"""
import os
import boto3
from botocore.exceptions import ClientError

REGION     = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMODB_MUSIC_TABLE", "Music")

dynamodb = boto3.client("dynamodb", region_name=REGION)


def create_table():
    print(f"Creating table '{TABLE_NAME}'...")
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "artist",     "KeyType": "HASH"},
                {"AttributeName": "title_year", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "artist",     "AttributeType": "S"},
                {"AttributeName": "title_year", "AttributeType": "S"},
                {"AttributeName": "year",       "AttributeType": "N"},  # Number — matches Java MusicCreateTable
                {"AttributeName": "title",      "AttributeType": "S"},
            ],
            LocalSecondaryIndexes=[
                {
                    "IndexName": "year-index",
                    "KeySchema": [
                        {"AttributeName": "artist", "KeyType": "HASH"},
                        {"AttributeName": "year",   "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "title-index",
                    "KeySchema": [
                        {"AttributeName": "title",  "KeyType": "HASH"},
                        {"AttributeName": "artist", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=TABLE_NAME)
        print(f"  Table '{TABLE_NAME}' created with LSI 'year-index' and GSI 'title-index'.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"  Table '{TABLE_NAME}' already exists — skipping creation.")
        else:
            raise


def create_subscriptions_table():
    """Also creates the Subscriptions table used by the subscription handlers."""
    subs_table = os.environ.get("DYNAMODB_SUBSCRIPTIONS_TABLE", "Subscriptions")
    print(f"Creating table '{subs_table}'...")
    try:
        dynamodb.create_table(
            TableName=subs_table,
            KeySchema=[
                {"AttributeName": "email",   "KeyType": "HASH"},
                {"AttributeName": "song_id", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "email",   "AttributeType": "S"},
                {"AttributeName": "song_id", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=subs_table)
        print(f"  Table '{subs_table}' created.")
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"  Table '{subs_table}' already exists — skipping creation.")
        else:
            raise


if __name__ == "__main__":
    create_table()
    create_subscriptions_table()
    print("All tables ready.")

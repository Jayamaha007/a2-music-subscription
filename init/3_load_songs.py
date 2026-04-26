"""
Reads 2026a2_songs.json and loads all song records into the DynamoDB `music` table.
Designed to be idempotent — re-running will not duplicate records.
"""
import boto3
import json

# TODO: implement batch-write loading of songs from 2026a2_songs.json

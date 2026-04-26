"""
Creates the DynamoDB `music` table with the correct PK/SK key schema,
at least one GSI, and at least one LSI.
Run once during Phase 4 initialisation before loading songs.
"""
import boto3

# TODO: implement table creation with GSI and LSI

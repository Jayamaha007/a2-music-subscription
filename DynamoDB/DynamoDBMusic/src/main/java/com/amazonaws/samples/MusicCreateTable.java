package com.amazonaws.samples;

import java.util.Arrays;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.*;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.dynamodbv2.model.*;

public class MusicCreateTable {

    public static void main(String[] args) throws Exception {

        // FIX: Use AWS instead of localhost
        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard().
                withRegion(Regions.US_EAST_1).
                withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        String tableName = "Music";

        try {
            System.out.println("Creating Music table with GSI + LSI...");

            CreateTableRequest request = new CreateTableRequest()
                    .withTableName(tableName)

                    // Primary Key
                    .withKeySchema(
                            new KeySchemaElement("artist", KeyType.HASH),
                            new KeySchemaElement("title_year", KeyType.RANGE)
                    )

                    // Attributes (IMPORTANT: must include all index keys)
                    .withAttributeDefinitions(
                            new AttributeDefinition("artist", ScalarAttributeType.S),
                            new AttributeDefinition("title_year", ScalarAttributeType.S),
                            new AttributeDefinition("title", ScalarAttributeType.S),
                            new AttributeDefinition("year", ScalarAttributeType.N)
                    )

                    // LSI (artist + year)
                    .withLocalSecondaryIndexes(
                            new LocalSecondaryIndex()
                                    .withIndexName("year-index")
                                    .withKeySchema(
                                            new KeySchemaElement("artist", KeyType.HASH),
                                            new KeySchemaElement("year", KeyType.RANGE)
                                    )
                                    .withProjection(
                                            new Projection().withProjectionType(ProjectionType.ALL)
                                    )
                    )

                    // GSI (title + artist)
                    .withGlobalSecondaryIndexes(
                            new GlobalSecondaryIndex()
                                    .withIndexName("title-index")
                                    .withKeySchema(
                                            new KeySchemaElement("title", KeyType.HASH),
                                            new KeySchemaElement("artist", KeyType.RANGE)
                                    )
                                    .withProjection(
                                            new Projection().withProjectionType(ProjectionType.ALL)
                                    )
                                    .withProvisionedThroughput(
                                            new ProvisionedThroughput(5L, 5L)
                                    )
                    )

                    // Table throughput
                    .withProvisionedThroughput(
                            new ProvisionedThroughput(10L, 10L)
                    );

            Table table = dynamoDB.createTable(request);

            System.out.println("Waiting for table to become ACTIVE...");
            table.waitForActive();

            System.out.println("Music table created successfully with GSI + LSI");

        } catch (Exception e) {
            System.err.println("Error creating table:");
            e.printStackTrace();
        }
    }
}
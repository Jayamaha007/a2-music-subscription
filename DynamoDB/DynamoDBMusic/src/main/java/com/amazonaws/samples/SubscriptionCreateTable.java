package com.amazonaws.samples;

import java.util.Arrays;

import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.dynamodbv2.model.*;

public class SubscriptionCreateTable {

    public static void main(String[] args) throws Exception {

        // Use LabRole (NO ProfileCredentialsProvider)
        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        String tableName = "Subscriptions";

        try {
            System.out.println("Creating Subscriptions table...");

            Table table = dynamoDB.createTable(tableName,

                    // Composite Primary Key
                    Arrays.asList(
                            new KeySchemaElement("email", KeyType.HASH),     // Partition key
                            new KeySchemaElement("song_id", KeyType.RANGE)   // Sort key
                    ),

                    // Attribute Definitions
                    Arrays.asList(
                            new AttributeDefinition("email", ScalarAttributeType.S),
                            new AttributeDefinition("song_id", ScalarAttributeType.S)
                    ),

                    // Throughput
                    new ProvisionedThroughput(10L, 10L)
            );

            table.waitForActive();

            System.out.println("Subscriptions table created: "
                    + table.getDescription().getTableStatus());

        } catch (Exception e) {
            System.err.println("Error creating Subscriptions table:");
            e.printStackTrace();
        }
    }
}
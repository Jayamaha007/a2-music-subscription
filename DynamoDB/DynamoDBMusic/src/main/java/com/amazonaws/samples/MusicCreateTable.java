package com.amazonaws.samples;

import java.util.Arrays;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.amazonaws.services.dynamodbv2.model.AttributeDefinition;
import com.amazonaws.services.dynamodbv2.model.KeySchemaElement;
import com.amazonaws.services.dynamodbv2.model.KeyType;
import com.amazonaws.services.dynamodbv2.model.ProvisionedThroughput;
import com.amazonaws.services.dynamodbv2.model.ScalarAttributeType;

public class MusicCreateTable {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withEndpointConfiguration(
                        new AwsClientBuilder.EndpointConfiguration(
                                "http://localhost:8000",
                                Regions.US_EAST_1.getName()))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        String tableName = "Music";

        try {
            System.out.println("Creating Music table...");

            Table table = dynamoDB.createTable(tableName,
                    Arrays.asList(
                            new KeySchemaElement("artist", KeyType.HASH),      // Partition key
                            new KeySchemaElement("title_year", KeyType.RANGE) // Sort key
                    ),
                    Arrays.asList(
                            new AttributeDefinition("artist", ScalarAttributeType.S),
                            new AttributeDefinition("title_year", ScalarAttributeType.S)
                    ),
                    new ProvisionedThroughput(10L, 10L));

            table.waitForActive();
            System.out.println("Table created successfully!");

        } catch (Exception e) {
            System.err.println("Error creating table:");
            System.err.println(e.getMessage());
        }
    }
}
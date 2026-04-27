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

public class LoginCreateTable {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withEndpointConfiguration(
                        new AwsClientBuilder.EndpointConfiguration(
                                "http://localhost:8000",
                                Regions.US_EAST_1.getName()))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        String tableName = "LoginTable";

        try {
            System.out.println("Creating LoginTable...");

            Table table = dynamoDB.createTable(tableName,
                    Arrays.asList(
                            new KeySchemaElement("email", KeyType.HASH) // Partition key
                    ),
                    Arrays.asList(
                            new AttributeDefinition("email", ScalarAttributeType.S)
                    ),
                    new ProvisionedThroughput(10L, 10L));

            table.waitForActive();
            System.out.println("Table created successfully: " + table.getDescription().getTableStatus());

        } catch (Exception e) {
            System.err.println("Error creating table:");
            System.err.println(e.getMessage());
        }
    }
}
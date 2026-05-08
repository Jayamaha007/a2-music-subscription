package com.amazonaws.samples;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.*;
import com.amazonaws.services.dynamodbv2.document.*;

public class DeleteMusicTable {

    public static void main(String[] args) throws Exception {

        String tableName = "Music"; 

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard().
                withRegion(Regions.US_EAST_1).
                withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        try {
            System.out.println("Deleting table: " + tableName);

            Table table = dynamoDB.getTable(tableName);
            table.delete();

            table.waitForDelete();

            System.out.println("Table deleted successfully.");

        } catch (Exception e) {
            System.err.println("Unable to delete table:");
            System.err.println(e.getMessage());
        }
    }
}
package com.amazonaws.samples;

import java.io.File;
import java.util.Iterator;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.*;
import com.amazonaws.services.dynamodbv2.document.*;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.*;

public class LoginLoadData {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard().
                withRegion(Regions.US_EAST_1).
                withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);
        Table table = dynamoDB.getTable("LoginTable");

        JsonParser parser = new JsonFactory().createParser(new File("logindata.json"));
        JsonNode rootNode = new ObjectMapper().readTree(parser);
        Iterator<JsonNode> iter = rootNode.iterator();

        while (iter.hasNext()) {
            JsonNode node = iter.next();

            String email = node.path("email").asText();
            String username = node.path("user_name").asText();
            String password = node.path("password").asText();

            table.putItem(new Item()
                    .withPrimaryKey("email", email)
                    .withString("user_name", username)
                    .withString("password", password));

            System.out.println("Inserted: " + email);
        }

        parser.close();
    }
}
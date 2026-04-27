package com.amazonaws.samples;

import java.io.File;
import java.util.Iterator;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.Table;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class MusicLoadData {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withEndpointConfiguration(
                        new AwsClientBuilder.EndpointConfiguration(
                                "http://localhost:8000",
                                Regions.US_EAST_1.getName()))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);
        Table table = dynamoDB.getTable("Music");

        JsonParser parser = new JsonFactory().createParser(new File("2026a2_songs.json"));

        JsonNode rootNode = new ObjectMapper().readTree(parser);
        JsonNode songs = rootNode.path("songs");

        Iterator<JsonNode> iter = songs.iterator();

        ObjectNode currentNode;

        while (iter.hasNext()) {

            currentNode = (ObjectNode) iter.next();

            String title = currentNode.path("title").asText();
            String artist = currentNode.path("artist").asText();
            String year = currentNode.path("year").asText();
            String album = currentNode.path("album").asText();
            String imageUrl = currentNode.path("img_url").asText();

            // 🔥 Composite sort key to avoid duplicates
            String titleYear = title + "_" + year;

            try {
                table.putItem(new Item()
                        .withPrimaryKey("artist", artist, "title_year", titleYear)
                        .withString("title", title)
                        .withString("year", year)
                        .withString("album", album)
                        .withString("image_url", imageUrl));

                System.out.println("Inserted: " + title + " (" + year + ")");

            } catch (Exception e) {
                System.err.println("Error inserting: " + title);
                System.err.println(e.getMessage());
            }
        }

        parser.close();
    }
}
package com.amazonaws.samples;

import java.io.File;
import java.util.Iterator;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.*;
import com.amazonaws.services.dynamodbv2.document.*;
import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.*;

public class MusicLoadData {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard().
                withRegion(Regions.US_EAST_1).
                withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);
        Table table = dynamoDB.getTable("Music");

        JsonParser parser = new JsonFactory().createParser(new File("2026a2_songs.json"));
        JsonNode rootNode = new ObjectMapper().readTree(parser);
        JsonNode songs = rootNode.path("songs");

        Iterator<JsonNode> iter = songs.iterator();

        while (iter.hasNext()) {

            JsonNode node = iter.next();

            String title = node.path("title").asText();
            String artist = node.path("artist").asText();
            int year = node.path("year").asInt();
            String album = node.path("album").asText();

            String titleYear = title + "#" + year;

            table.putItem(new Item()
                    .withPrimaryKey("artist", artist, "title_year", titleYear)
                    .withString("title", title)
                    .withNumber("year", year)
                    .withString("album", album)
                    .withString("image_key",
                            artist.replaceAll("[^a-zA-Z0-9]", "_") + ".jpg"));

            System.out.println("Inserted: " + title);
        }

        parser.close();
    }
}
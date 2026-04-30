// Adapted from AWS MoviesQuery example for assignment requirements

package com.amazonaws.samples;

import java.util.HashMap;
import java.util.Iterator;

import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.*;
import com.amazonaws.services.dynamodbv2.document.spec.QuerySpec;

public class MusicQuery {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withEndpointConfiguration(
                        new AwsClientBuilder.EndpointConfiguration(
                                "http://localhost:8000",
                                Regions.US_EAST_1.getName()))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        Table table = dynamoDB.getTable("Music");

        // =====================================================
        // QUERY 1: Songs by artist + year (LSI)
        // =====================================================

        HashMap<String, String> nameMap = new HashMap<>();
        nameMap.put("#yr", "year");

        HashMap<String, Object> valueMap = new HashMap<>();
        valueMap.put(":artist", "Taylor Swift");
        valueMap.put(":year", 2008);

        QuerySpec querySpec = new QuerySpec()
                .withKeyConditionExpression("artist = :artist and #yr = :year")
                .withNameMap(nameMap)
                .withValueMap(valueMap);

        ItemCollection<QueryOutcome> items = null;
        Iterator<Item> iterator = null;
        Item item = null;

        try {
            System.out.println("Songs by Taylor Swift in 2008:");

            // Must query using LSI
            items = table.getIndex("year-index").query(querySpec);

            iterator = items.iterator();
            while (iterator.hasNext()) {
                item = iterator.next();
                System.out.println(item.getString("title") + " (" + item.getNumber("year") + ")");
            }

        } catch (Exception e) {
            System.err.println("Query failed");
            System.err.println(e.getMessage());
        }

        // =====================================================
        // QUERY 2: Songs by title (GSI)
        // =====================================================

        valueMap.clear();
        valueMap.put(":title", "Love Story");

        querySpec.withKeyConditionExpression("title = :title")
                .withValueMap(valueMap);

        try {
            System.out.println("\nSongs with title 'Love Story':");

            // ⚠Must use GSI
            items = table.getIndex("title-index").query(querySpec);

            iterator = items.iterator();
            while (iterator.hasNext()) {
                item = iterator.next();
                System.out.println(item.getString("artist") + " - " + item.getString("title"));
            }

        } catch (Exception e) {
            System.err.println("GSI query failed");
            System.err.println(e.getMessage());
        }
    }
}
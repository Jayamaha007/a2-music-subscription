package com.amazonaws.samples;

import java.util.HashMap;
import java.util.Iterator;

import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.*;
import com.amazonaws.services.dynamodbv2.document.spec.ScanSpec;

public class MusicScan {

    public static void main(String[] args) throws Exception {

        AmazonDynamoDB client = AmazonDynamoDBClientBuilder.standard()
                .withEndpointConfiguration(
                        new AwsClientBuilder.EndpointConfiguration(
                                "http://localhost:8000",
                                Regions.US_EAST_1.getName()))
                .build();

        DynamoDB dynamoDB = new DynamoDB(client);

        Table table = dynamoDB.getTable("Music");

        HashMap<String, String> nameMap = new HashMap<>();
        nameMap.put("#yr", "year");

        HashMap<String, Object> valueMap = new HashMap<>();
        valueMap.put(":artist", "Taylor Swift");
        valueMap.put(":album", "Fearless");
        valueMap.put(":year", 2008);

        ScanSpec scanSpec = new ScanSpec()
                .withFilterExpression("artist = :artist AND album = :album AND #yr = :year")
                .withNameMap(nameMap)
                .withValueMap(valueMap);

        ItemCollection<ScanOutcome> items = null;
        Iterator<Item> iterator = null;

        try {
            System.out.println("Scan: Taylor Swift - Fearless (2008)");

            items = table.scan(scanSpec);

            iterator = items.iterator();
            while (iterator.hasNext()) {
                Item item = iterator.next();
                System.out.println(item.getString("title") + " (" + item.getNumber("year") + ")");
            }

        } catch (Exception e) {
            System.err.println("Scan failed");
            System.err.println(e.getMessage());
        }
    }
}
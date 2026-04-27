package com.amazonaws.samples;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.URL;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class UploadArtistImagesToS3 {

    public static void main(String[] args) throws Exception {

        String bucketName = "chathraka-music-images-2026"; //

        AmazonS3 s3 = AmazonS3ClientBuilder.standard()
                .withRegion(Regions.US_EAST_1)
                .withCredentials(new ProfileCredentialsProvider("default"))
                .build();

        // Create bucket if not exists
        if (!s3.doesBucketExistV2(bucketName)) {
            System.out.println("Creating bucket: " + bucketName);
            s3.createBucket(bucketName);
        } else {
            System.out.println("Bucket already exists");
        }

        JsonParser parser = new JsonFactory().createParser(new File("2026a2_songs.json"));
        JsonNode rootNode = new ObjectMapper().readTree(parser);
        JsonNode songs = rootNode.path("songs");

        Iterator<JsonNode> iter = songs.iterator();

        Set<String> processedArtists = new HashSet<>();

        while (iter.hasNext()) {

            JsonNode node = iter.next();

            String artist = node.path("artist").asText();
            String imageUrl = node.path("img_url").asText();

            if (processedArtists.contains(artist)) {
                continue;
            }

            try {
                System.out.println("Processing: " + artist);

                // Download image
                URL url = new URL(imageUrl);
                InputStream in = url.openStream();

                String fileName = artist.replaceAll("[^a-zA-Z0-9]", "_") + ".jpg";
                File file = new File(fileName);

                FileOutputStream out = new FileOutputStream(file);

                byte[] buffer = new byte[4096];
                int bytesRead;

                while ((bytesRead = in.read(buffer)) != -1) {
                    out.write(buffer, 0, bytesRead);
                }

                in.close();
                out.close();

                // Upload to S3
                s3.putObject(new PutObjectRequest(bucketName, fileName, file));

                System.out.println("Uploaded: " + fileName);

                processedArtists.add(artist);

                // Optional cleanup
                file.delete();

            } catch (Exception e) {
                System.err.println("Error processing: " + artist);
                System.err.println(e.getMessage());
            }
        }

        parser.close();
        System.out.println("All images uploaded!");
    }
}
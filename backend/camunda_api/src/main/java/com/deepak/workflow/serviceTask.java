package com.deepak.workflow;

import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.JavaDelegate;

import java.io.OutputStream;
import java.io.InputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;
import java.util.logging.Logger;
import org.json.JSONObject;

public class serviceTask implements JavaDelegate {

    private final Logger logger = Logger.getLogger(serviceTask.class.getName());

    @Override
    public void execute(DelegateExecution execution) throws Exception {
        // Load the variables from the process instance
        String container = (String) execution.getVariable("container");
        String port = (String) execution.getVariable("port");
        String route = (String) execution.getVariable("route");
        String payload = (String) execution.getVariable("payload");

        logger.info("Container: " + container);
        logger.info("Port: " + port);
        logger.info("Route: " + route);
        logger.info("Payload: " + payload);

        if (container == null || port == null || route == null) {
            throw new IllegalArgumentException("Container, port, or route is missing.");
        }

        String targetUrl = "http://" + container + ":" + port + "/" + route;
        logger.info("Target URL: " + targetUrl);

        HttpURLConnection conn = null;

        try {
            URL url = new URL(targetUrl);
            conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            if (payload != null && !payload.isEmpty()) {
                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = payload.getBytes("utf-8");
                    os.write(input, 0, input.length);
                    logger.info("Payload sent successfully.");
                }
            }

            int responseCode = conn.getResponseCode();
            execution.setVariable("status_code", responseCode);
            logger.info("HTTP Response Code: " + responseCode);

            try (InputStream is = conn.getInputStream()) {
                Scanner scanner = new Scanner(is).useDelimiter("\\A");
                String responseBody = scanner.hasNext() ? scanner.next() : "";
                execution.setVariable("response_body", responseBody);
                logger.info("HTTP Response Body: " + responseBody);

                JSONObject json = new JSONObject(responseBody);
                boolean flag = json.optBoolean("flag", false);
                execution.setVariable("flag", flag);
                logger.info("Parsed Flag Value is: " + flag);
            }

        } catch (IOException e) {
            if (conn != null) {
                InputStream errorStream = conn.getErrorStream();
                if (errorStream != null) {
                    Scanner errorScanner = new Scanner(errorStream).useDelimiter("\\A");
                    String errorResponse = errorScanner.hasNext() ? errorScanner.next() : "";
                    logger.severe("Error response body: " + errorResponse);
                }
            }
            logger.severe("Error while calling the API: " + e.getMessage());
            throw new RuntimeException("API call failed", e);
        }
    }
}
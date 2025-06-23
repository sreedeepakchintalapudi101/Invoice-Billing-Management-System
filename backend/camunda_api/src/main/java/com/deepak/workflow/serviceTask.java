package com.deepak.workflow;

import org.camunda.bpm.engine.delegate.DelegateExecution;
import org.camunda.bpm.engine.delegate.JavaDelegate;
import org.springframework.stereotype.Component;

import java.io.OutputStream;
import java.io.InputStream;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;
import java.util.logging.Logger;

@Component("ServiceTask")
public class ServiceTask implements JavaDelegate {

    private final Logger logger = Logger.getLogger(ServiceTask.class.getName());

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

        // Validate
        if (container == null || port == null || route == null) {
            throw new IllegalArgumentException("Container, port, or route is missing.");
        }

        // Construct the URL
        String targetUrl = "http://" + container + ":" + port + "/" + route;
        logger.info("Target URL: " + targetUrl);

        try {
            URL url = new URL(targetUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            // Send payload
            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = payload.getBytes("UTF-8");
                os.write(input, 0, input.length);
            }

            int responseCode = conn.getResponseCode();
            execution.setVariable("status_code", responseCode);
            logger.info("HTTP Response Code: " + responseCode);

            // Read response body
            String responseBody;
            try (InputStream is = conn.getInputStream()) {
                Scanner scanner = new Scanner(is).useDelimiter("\\A");
                responseBody = scanner.hasNext() ? scanner.next() : "";
                execution.setVariable("response_body", responseBody);
                logger.info("HTTP Response Body: " + responseBody);
            }

        } catch (IOException e) {
            logger.severe("Error while calling the API: " + e.getMessage());
            throw new RuntimeException("API call failed", e);
        }
    }
}

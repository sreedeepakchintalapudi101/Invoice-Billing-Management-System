package com.deepak;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import java.util.logging.Logger;

@SpringBootApplication
public class SpringBootApplication{

    private static final Logger logger = Logger.getLogger(CamundaApiApplication.class.getName());

    public static void main(String[] args) {
        SpringApplication.run(CamundaApiApplication.class, args);
        logger.info("Camunda API Application started successfully.");
    }
}

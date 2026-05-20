package com.example.productreview;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;

@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
public class ProductReviewApplication {
    public static void main(String[] args) {
        SpringApplication.run(ProductReviewApplication.class, args);
    }
}

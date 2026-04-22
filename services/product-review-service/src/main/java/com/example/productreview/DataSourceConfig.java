package com.example.productreview;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;
import java.net.URI;

@Configuration
public class DataSourceConfig {

    @Value("${DATABASE_URL}")
    private String databaseUrl;

    @Bean
    public DataSource dataSource() {
        // Input: postgresql://user:password@host:port/dbname?params
        URI uri = URI.create(databaseUrl.replaceFirst("^postgresql://", "http://"));

        String host = uri.getHost();
        int port = uri.getPort() == -1 ? 5432 : uri.getPort();
        String db = uri.getPath().replaceFirst("^/", "");
        String userInfo = uri.getUserInfo(); // "user:password"
        String user = userInfo.split(":")[0];
        String password = userInfo.substring(user.length() + 1);

        String jdbcUrl = String.format("jdbc:postgresql://%s:%d/%s", host, port, db);

        return DataSourceBuilder.create()
                .url(jdbcUrl)
                .username(user)
                .password(password)
                .build();
    }
}

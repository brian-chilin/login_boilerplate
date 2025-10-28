package com.example.demo;


import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {

    @Value("${db.host}")
    private String host;
    @Value("${db.name}")
    private String name;
    @Value("${db.password}")
    private String pass;
    @Value("${db.port}")
    private int port;
    @Value("${db.user}")
    private String user;

    @Bean
    public DataSource dataSource() {
        String url = "jdbc:postgresql://" + host + ":" + port + "/" + name;

        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(url);
        config.setUsername(user);
        config.setPassword(pass);
        config.setDriverClassName("org.postgresql.Driver");

        config.setMaximumPoolSize(5);
        config.setMinimumIdle(2);
        config.setIdleTimeout(30000);
        config.setConnectionTimeout(10000);

        return new HikariDataSource(config);
    }
}

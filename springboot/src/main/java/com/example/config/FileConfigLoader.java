package com.example.config;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.env.EnvironmentPostProcessor;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.core.env.MapPropertySource;

import java.io.IOException;
import java.nio.file.*;
import java.util.HashMap;
import java.util.Map;

public class FileConfigLoader implements EnvironmentPostProcessor {

    private static final Path CONFIG_DIR = Path.of("/etc/config");

    @Override
    public void postProcessEnvironment(ConfigurableEnvironment environment, SpringApplication application) {
        Map<String, Object> props = new HashMap<>();

        try {
            if (Files.exists(CONFIG_DIR)) {
                Files.walk(CONFIG_DIR)
                     .filter(Files::isRegularFile)
                     .forEach(path -> {
                         try {
                             String relative = CONFIG_DIR.relativize(path)
                                     .toString()
                                     .replace(FileSystems.getDefault().getSeparator(), ".");
                             String value = Files.readString(path).trim();
                             props.put(relative, value);
                         } catch (IOException ignored) {}
                     });
            }
        } catch (IOException ignored) {}

        environment.getPropertySources()
                   .addFirst(new MapPropertySource("fileConfig", props));
    }
}

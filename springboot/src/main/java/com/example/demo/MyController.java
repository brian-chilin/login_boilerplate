package com.example.demo;

import java.util.Map;
import java.util.HashMap;
import java.io.StringReader;
import java.time.LocalDateTime;

import com.samskivert.mustache.Mustache;
import com.samskivert.mustache.Template;

import de.mkammerer.argon2.Argon2;
import de.mkammerer.argon2.Argon2Factory;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;


@RestController
public class MyController {

    private final Template compiledTemplate;
    private final JdbcTemplate jdbcTemplate;
    private final Argon2 argon2;
    public MyController(
        @Value("${html.html_template: failed to find html.html_template}") String htmlTemplate,
        JdbcTemplate jdbcTemplate
    ) {
        Mustache.Compiler compiler = Mustache.compiler();
        this.compiledTemplate = compiler.compile(new StringReader(htmlTemplate));
        this.jdbcTemplate = jdbcTemplate;
        this.argon2 = Argon2Factory.create(Argon2Factory.Argon2Types.ARGON2id);
    }

    public HashMap<String, String> get_standard_context() {
        HashMap<String, String> context = new HashMap<>();
        context.put("CURRENT_TIME", LocalDateTime.now().toString());
        context.put("FORM_USERNAME_VALUE", "");
        context.put("REQUEST_RESULT", "");
        context.put("STATUS", "SpringBoot");

        StringBuilder b = new StringBuilder();
        jdbcTemplate.query(
            "SELECT * FROM users ORDER BY id;",
            (rs) -> {
                b.append("<tr><td>");
                b.append(rs.getInt(1));
                b.append("</td><td>");
                b.append(rs.getString(2));
                b.append("</td><td>");
                b.append(rs.getString(3));
                b.append("</td><td>");
                b.append(rs.getString(4));
                b.append("</td></tr>");
            }
        );
        context.put("TABLE_CONTENTS", b.toString());
        return context;
    }

    @GetMapping(value = "/", produces = "text/html")
    public String getIndex() {
        long start = System.nanoTime();
        Map<String, String> context = get_standard_context();
        context.put(
            "STATUS",
            ((System.nanoTime() - start) / 1_000_000.0)+"ms from SpringBoot"
        );
        return compiledTemplate.execute(context);
    }

    @PostMapping(value = "/", produces = "text/html")
    public String postIndex(
        @RequestParam String username,
        @RequestParam String password
    ) {
        long start = System.nanoTime();
        Map<String, String> context = get_standard_context();

        context.put("FORM_USERNAME_VALUE", username);
        
        if(!username.isBlank() && !password.isBlank()) {
            context.put("REQUEST_RESULT", "❌ Invalid Credentials");
            try {
                String hash = jdbcTemplate.queryForObject(
                    "SELECT password FROM users WHERE username = ?",
                    String.class,
                    username
                );

                if (argon2.verify(hash, password.toCharArray())) {
                    context.put("REQUEST_RESULT", "✅ Credentials Verified");
                }
            } catch (EmptyResultDataAccessException e) {
                // No user found
                System.out.println("no user found");
            }
        }

        context.put(
            "STATUS",
            ((System.nanoTime() - start) / 1_000_000.0)+"ms from SpringBoot"
        );
        return compiledTemplate.execute(context);
    }

}

package com.example.demo;

import java.util.Map;
import java.util.HashMap;
import java.io.StringReader;
import java.time.LocalDateTime;

import com.samskivert.mustache.Mustache;
import com.samskivert.mustache.Template;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MyController {

    private final Template compiledTemplate;
    public MyController(@Value("${html.html_template: failed to find html.html_template}") String htmlTemplate) {
        Mustache.Compiler compiler = Mustache.compiler();
        this.compiledTemplate = compiler.compile(new StringReader(htmlTemplate));
    }

    public HashMap<String, String> get_standard_context() {
        HashMap<String, String> context = new HashMap<>();
        context.put("CURRENT_TIME", LocalDateTime.now().toString());
        context.put("TABLE_CONTENTS", "");
        context.put("FORM_USERNAME_VALUE", "");
        context.put("REQUEST_RESULT", "");
        context.put("STATUS", "SpringBoot");
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
        context.put(
            "STATUS",
            ((System.nanoTime() - start) / 1_000_000.0)+"ms from SpringBoot"
        );
        return compiledTemplate.execute(get_standard_context());
    }

}

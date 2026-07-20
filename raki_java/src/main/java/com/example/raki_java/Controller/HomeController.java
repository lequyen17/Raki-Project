package com.example.raki_java.Controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "Chào bạn! Ứng dụng Spring Boot đã chạy thành công rồi nhé.";
    }
}
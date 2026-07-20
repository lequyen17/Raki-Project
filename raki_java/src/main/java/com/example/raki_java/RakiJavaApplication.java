package com.example.raki_java;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.jdbc.autoconfigure.DataSourceAutoConfiguration;

@SpringBootApplication(exclude = { DataSourceAutoConfiguration.class })
public class RakiJavaApplication {

	public static void main(String[] args) {
		SpringApplication.run(RakiJavaApplication.class, args);
	}

}

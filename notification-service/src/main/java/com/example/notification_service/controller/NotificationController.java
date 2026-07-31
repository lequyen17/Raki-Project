package com.example.notification_service.controller;

import com.example.notification_service.dto.NotificationDto;
import com.example.notification_service.service.NotificationService;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Base64;
import java.util.List;

@RestController
@RequiredArgsConstructor
@Slf4j
public class NotificationController {

    private final NotificationService notificationService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @GetMapping("/")
    public ResponseEntity<List<NotificationDto>> getNotifications(
            @RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String authorizationHeader) {

        if (authorizationHeader == null || !authorizationHeader.startsWith("Bearer ")) {
            log.warn("Missing or invalid Authorization header");
            return ResponseEntity.status(401).build();
        }

        String token = authorizationHeader.substring(7);
        Long userId = extractUserIdFromToken(token);

        if (userId == null) {
            log.warn("Could not extract user ID from token");
            return ResponseEntity.status(401).build();
        }

        List<NotificationDto> notifications = notificationService.getNotificationsByUserId(userId);
        return ResponseEntity.ok(notifications);
    }

    private Long extractUserIdFromToken(String token) {
        try {
            String[] chunks = token.split("\\.");
            if (chunks.length < 2) {
                return null;
            }
            Base64.Decoder decoder = Base64.getUrlDecoder();
            String payload = new String(decoder.decode(chunks[1]));
            JsonNode payloadNode = objectMapper.readTree(payload);

            // Try common claims for user ID like "user_id", "sub", or "id"
            if (payloadNode.has("user_id")) {
                return payloadNode.get("user_id").asLong();
            } else if (payloadNode.has("sub")) {
                return Long.parseLong(payloadNode.get("sub").asText());
            } else if (payloadNode.has("id")) {
                return payloadNode.get("id").asLong();
            }
        } catch (Exception e) {
            log.error("Error parsing JWT payload", e);
        }
        return null;
    }
}

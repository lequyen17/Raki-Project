package com.example.notification_service.config;

import com.example.notification_service.dto.NotificationDto;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.io.IOException;
import java.util.Base64;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
@Slf4j
@RequiredArgsConstructor
public class NotificationWebSocketHandler extends TextWebSocketHandler {

    // Thread-safe map to store user sessions
    private final Map<Long, WebSocketSession> userSessions = new ConcurrentHashMap<>();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        Long userId = extractUserIdFromSession(session);
        if (userId != null) {
            userSessions.put(userId, session);
            log.info("WebSocket connection established for userId: {}", userId);
        } else {
            log.warn("WebSocket connection established but no valid userId found. Closing session.");
            session.close(CloseStatus.BAD_DATA);
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        Long userId = extractUserIdFromSession(session);
        if (userId != null) {
            userSessions.remove(userId);
            log.info("WebSocket connection closed for userId: {}", userId);
        }
    }

    public void sendNotificationToUser(Long userId, NotificationDto notificationDto) {
        WebSocketSession session = userSessions.get(userId);
        if (session != null && session.isOpen()) {
            try {
                String payload = objectMapper.writeValueAsString(notificationDto);
                session.sendMessage(new TextMessage(payload));
                log.info("Sent notification to userId: {}", userId);
            } catch (IOException e) {
                log.error("Failed to send notification to userId: {}", userId, e);
            }
        } else {
            log.debug("No active WebSocket session found for userId: {}", userId);
        }
    }

    private Long extractUserIdFromSession(WebSocketSession session) {
        try {
            // Extract the token from the query params (e.g. ?token=...)
            String query = session.getUri().getQuery();
            if (query != null && query.contains("token=")) {
                String[] params = query.split("&");
                for (String param : params) {
                    if (param.startsWith("token=")) {
                        String token = param.substring(6);
                        return extractUserIdFromToken(token);
                    }
                }
            }
        } catch (Exception e) {
            log.error("Error extracting userId from session URI", e);
        }
        return null;
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

            if (payloadNode.has("user_id")) {
                return payloadNode.get("user_id").asLong();
            } else if (payloadNode.has("sub")) {
                return Long.parseLong(payloadNode.get("sub").asText());
            } else if (payloadNode.has("id")) {
                return payloadNode.get("id").asLong();
            }
        } catch (Exception e) {
            log.error("Error parsing JWT payload in WebSocket handler", e);
        }
        return null;
    }
}

package com.example.notification_service.service;

import com.example.notification_service.config.NotificationWebSocketHandler;
import com.example.notification_service.dto.NotificationDto;
import com.example.notification_service.dto.NotificationEvent;
import com.example.notification_service.entity.Notification;
import com.example.notification_service.repository.NotificationRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class NotificationService {

    private final NotificationRepository notificationRepository;
    private final NotificationWebSocketHandler webSocketHandler;

    public void processNotificationEvent(NotificationEvent event) {
        log.info("Processing notification event: {}", event);

        // 1. Save to DB
        Notification notification = Notification.builder()
                .userId(event.getUserId())
                .type(event.getType())
                .title(event.getTitle())
                .content(event.getContent())
                .actionUrl(event.getActionUrl())
                .build();
        
        Notification saved = notificationRepository.save(notification);
        
        // 2. Map to DTO
        NotificationDto dto = mapToDto(saved);
        
        // 3. Send to WebSocket via custom handler
        webSocketHandler.sendNotificationToUser(event.getUserId(), dto);
    }
    
    @Transactional
    public List<NotificationDto> getNotificationsByUserId(Long userId) {
        List<Notification> notifications = notificationRepository.findByUserIdOrderByCreatedAtDesc(userId);
        
        boolean hasUnread = false;
        for (Notification notification : notifications) {
            if (Boolean.FALSE.equals(notification.getIsRead())) {
                notification.setIsRead(true);
                hasUnread = true;
            }
        }
        
        if (hasUnread) {
            notificationRepository.saveAll(notifications);
        }
        
        return notifications.stream()
                .map(this::mapToDto)
                .collect(Collectors.toList());
    }

    private NotificationDto mapToDto(Notification notification) {
        return NotificationDto.builder()
                .id(notification.getId())
                .userId(notification.getUserId())
                .type(notification.getType())
                .title(notification.getTitle())
                .content(notification.getContent())
                .isRead(notification.getIsRead())
                .actionUrl(notification.getActionUrl())
                .createdAt(notification.getCreatedAt())
                .build();
    }
}

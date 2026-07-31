package com.example.notification_service.service;

import com.example.notification_service.config.RabbitMQConfig;
import com.example.notification_service.dto.NotificationEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class NotificationListener {

    private final NotificationService notificationService;

    @RabbitListener(queues = RabbitMQConfig.QUEUE_NAME)
    public void handleNotificationEvent(NotificationEvent event) {
        try {
            log.info("Received notification event: {}", event);
            notificationService.processNotificationEvent(event);
        } catch (Exception e) {
            log.error("Error processing notification event", e);
        }
    }
}

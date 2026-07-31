import json
import logging
import pika
from django.conf import settings

logger = logging.getLogger(__name__)

def publish_notification_event(user_id, noti_type, title, content, action_url=None):
    """
    Publishes a notification event to RabbitMQ.
    The payload matches the Spring Boot NotificationEvent class.
    """
    try:
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Ensure the exchange exists (Spring Boot creates it, but good to be safe)
        channel.exchange_declare(exchange='core.exchange', exchange_type='topic', durable=True)

        payload = {
            "userId": user_id,
            "type": noti_type,
            "title": title,
            "content": content,
            "actionUrl": action_url
        }

        # Routing key determines where it goes. 
        # Spring Boot NotificationService listens to "notification.#"
        routing_key = f"notification.{noti_type.lower()}"

        channel.basic_publish(
            exchange='core.exchange',
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"Published notification event to RabbitMQ: {payload}")
        connection.close()
        
    except Exception as e:
        logger.error(f"Failed to publish notification to RabbitMQ: {str(e)}")

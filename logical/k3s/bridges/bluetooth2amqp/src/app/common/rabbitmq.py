import pika
import logging
import env
from typing import Optional

if not env.rabbitmq_host:
    raise ValueError("RABBITMQ_HOST environment variable is not set")

params = pika.URLParameters(env.rabbitmq_host)
exchange = "bluetooth"


def bluetooth_publish(
    routing_key: str,
    payload: bytes,
    headers: Optional[dict] = None,
): 
    with pika.BlockingConnection(params) as connection:
        channel = connection.channel()
        properties = pika.BasicProperties(headers=headers) if headers else None
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=payload,
            properties=properties,
        )
    logging.debug(
        f"Message published to RabbitMQ exchange '{exchange}' with routing key '{routing_key}'"
    ) 

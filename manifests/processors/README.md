# Streaming apps
  

https://www.photoprism.app/features


#

channel.exchange_declare("mqtt.topic", "topic", durable=True)
channel.basic_publish(
    exchange="mqtt.topic",
    routing_key="sensors/airthings/temperature",
    body=b"23.5"
)
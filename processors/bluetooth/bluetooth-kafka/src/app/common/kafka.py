from kafka import KafkaProducer
import logging
import env 

producer = KafkaProducer(
    bootstrap_servers=env.kafka_broker
) 

def produce(key: str, payload: bytes): 
    try: 
        future = producer.send(
            'bluetooth',
            key=key.encode('utf-8') if key else None,
            value=payload
        )
        record_metadata = future.get(timeout=10)
        producer.flush()
        logging.debug(f"Message delivered to {record_metadata.topic} [{record_metadata.partition}]")
    except Exception as e:
        logging.error(f"Delivery failed: {e}")

import json
import logging
from kafka import KafkaConsumer
import paho.mqtt.client as mqtt
import env as environment

# Kafka configuration
KAFKA_BROKER = environment.kafka_broker
KAFKA_TOPIC = environment.kafka_topic

# MQTT configuration
MQTT_BROKER = environment.mqtt_broker
MQTT_PORT = environment.mqtt_port
MQTT_TOPIC = environment.mqtt_topic
 
logging.basicConfig(level=getattr(logging, environment.log_level, logging.INFO), format='%(asctime)s %(levelname)s %(message)s')

def consume_from_kafka():
    """Consume messages from Kafka and publish to MQTT."""

    logging.info(f"Connecting to Kafka broker: {KAFKA_BROKER}")

    # Kafka consumer configuration
    kafka_consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER, 
        auto_offset_reset='earliest'
    ) 
    mqtt_client = mqtt.Client()

    try:
        kafka_consumer.subscribe([KAFKA_TOPIC])
        logging.info(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")

        # MQTT client setup
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()

        logging.info(f"Connected to MQTT broker: {MQTT_BROKER}")
        logging.info(f"Publishing messages to MQTT topic: {MQTT_TOPIC}")
        for msg in kafka_consumer:
            try:
                # Decode the Kafka message payload
                message_payload = json.loads(msg.value.decode('utf-8'))
                resource_logs = message_payload.get("resourceLogs", [])

                for resource_log in resource_logs: 
                    resource = resource_log.get("resource", {})
                    attributes = resource.get("attributes", [])
                    container_name = next(
                        (attr["value"]["stringValue"] for attr in attributes if attr["key"] == "k8s.container.name"), None
                    )
                    scope_logs = resource_log.get("scopeLogs", [])

                    for scope_log in scope_logs:
                        log_records = scope_log.get("logRecords", [])
                        for log_record in log_records:
                            # Extract log details
                            time_unix_nano = log_record.get("timeUnixNano", "")
                            body = log_record.get("body", {}).get("stringValue", "")
                            log_attributes = log_record.get("attributes", [])

                            # Format log attributes
                            formatted_attributes = {
                                attr["key"]: attr["value"]["stringValue"]
                                for attr in log_attributes
                                if "key" in attr and "value" in attr and "stringValue" in attr["value"]
                            }

                            # Construct a formatted log message
                            formatted_log = {
                                "timestamp": time_unix_nano,
                                "body": body,
                                "attributes": formatted_attributes,
                            }

                            if "error" in body:  
                                mqtt_client.publish(MQTT_TOPIC + container_name, json.dumps(body), qos=1, retain=True) 

            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                logging.error(f"Error processing message: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        logging.info("Closing Kafka consumer and MQTT client.")
        kafka_consumer.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

if __name__ == "__main__":
    consume_from_kafka()
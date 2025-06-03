import os
import json
import logging
from kafka import KafkaConsumer
import psycopg2
from psycopg2 import sql, OperationalError
import env as environment
 
logging.basicConfig(level=getattr(logging, environment.log_level, logging.INFO), format='%(asctime)s %(levelname)s %(message)s')

# Validate environment variables
required_env = ["KAFKA_BROKER", "KAFKA_TOPIC", "DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
missing = [var for var in required_env if not os.environ.get(var)]
if missing:
    logging.error(f"Missing required environment variables: {', '.join(missing)}")
    exit(1)
 
KAFKA_TOPICS = [environment.kafka_topic]

def main(): 
    kafka_consumer = KafkaConsumer( 
        bootstrap_servers=[environment.kafka_broker],
        auto_offset_reset='earliest',
    ) 

    try:
        with psycopg2.connect(
            host=environment.db_host, 
            port=environment.db_port, 
            user=environment.db_user, 
            password=environment.db_password, 
            dbname=environment.db_name
        ) as conn:
            with conn.cursor() as cur:
                    kafka_consumer.subscribe(KAFKA_TOPICS)
                    logging.info(f"Subscribed to Kafka topic: {KAFKA_TOPICS}")
                    for msg in kafka_consumer:
                        try:
                            # Check if message key exists and starts with 'bluetooth'
                            if not msg.key or not msg.key.decode('utf-8').startswith('bluetooth'):
                                logging.debug(f"Skipping message with key: {msg.key} from topic: {msg.topic}")
                                continue

                            raw_value = msg.value.decode('utf-8')
                            if not raw_value.strip():
                                logging.error("Received empty message from Kafka, skipping.")
                                continue 
                            cur.execute(
                                sql.SQL("INSERT INTO sensor (data) VALUES (%s)"),
                                [raw_value]
                            )
                            conn.commit()
                            logging.debug("Inserted message into sensordb")
                        except Exception as db_err:
                            logging.error(f"Database error: {db_err}")
                            conn.rollback()
    except OperationalError as db_conn_err:
        logging.error(f"Could not connect to database: {db_conn_err}")
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully.")
    finally:
        kafka_consumer.close()
        logging.info("Kafka consumer closed.")

if __name__ == "__main__":
    main()
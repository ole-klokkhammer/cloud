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

KAFKA_BROKER = environment.kafka_broker
KAFKA_TOPIC = environment.kafka_topic
DB_HOST = environment.db_host
DB_PORT = environment.db_port
DB_USER = environment.db_user
DB_PASSWORD = environment.db_password
DB_NAME = environment.db_name

def main(): 
    kafka_consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='earliest',
    ) 

    try:
        with psycopg2.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
        ) as conn:
            with conn.cursor() as cur:
                    kafka_consumer.subscribe([KAFKA_TOPIC])
                    logging.info(f"Subscribed to Kafka topic: {KAFKA_TOPIC}")
                    for msg in kafka_consumer:
                        try:
                            raw_value = msg.value.decode('utf-8')
                            if not raw_value.strip():
                                logging.error("Received empty message from Kafka, skipping.")
                                continue 
                            cur.execute(
                                sql.SQL("INSERT INTO sensor (data) VALUES (%s)"),
                                [raw_value]
                            )
                            conn.commit()
                            logging.info("Inserted message into sensordb")
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
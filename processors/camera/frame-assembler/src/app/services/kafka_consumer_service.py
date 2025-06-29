import logging
from typing import Callable, Optional
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import CorruptRecordError
from kafka.consumer.fetcher import ConsumerRecord


class KafkaConsumerService:
    def __init__(
        self,
        topic: str,
        bootstrap_servers: str,
        group_id: str,
        on_message: Optional[Callable[[ConsumerRecord], None]] = None,
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.on_message = on_message

        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda x: x,  # Keep as bytes
            group_id=self.group_id,
            enable_auto_commit=False,  # Disable auto-commit to reduce latency
            fetch_min_bytes=1,
            fetch_max_wait_ms=1,  # Reduce wait time for new messages
        )
        self.dead_letter_producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers
        )

    def start(self):
        logging.info("Starting consuming from kafka...")

        while True:
            try:

                for message in self.consumer:
                    try:
                        if self.on_message:
                            self.on_message(message)
                            self.consumer.commit()
                        else:
                            logging.warning(
                                "No on_message handler defined, skipping message."
                            )
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")
                        self.try_send_to_dead_letter_topic(message)
                        self.skip_message(message)
                        continue
            except CorruptRecordError as e:
                logging.error(f"Corrupt record encountered, skipping: {e}")
                self.skip_message(commit=True)
                continue

    def stop(self):
        logging.info("Stopping Kafka consumer...")
        try:
            self.consumer.close()
            logging.info("Kafka consumer stopped.")
        except Exception as e:
            logging.error(f"Error while closing Kafka consumer: {e}")

    def skip_message(self, offset: int = 1, commit: bool = True):
        """
        Skip the current message by seeking to the next offset.
        """

        for tp in self.consumer.assignment():
            current_offset = self.consumer.position(tp)
            self.consumer.seek(tp, current_offset + offset)

        if commit:
            self.consumer.commit()

        logging.info(f"Skipped current message and moved to next offset by {offset}.")

    def try_send_to_dead_letter_topic(self, message: ConsumerRecord):
        """
        Send the current message to a dead-letter topic.
        """
        try:
            dead_letter_topic = message.topic + "_dead_letter"
            self.dead_letter_producer.send(
                topic=message.topic + "_dead_letter",
                value=message.value,
                key=message.key,
                headers=message.headers,
            )
            logging.info(f"Sent message to dead-letter topic: {dead_letter_topic}")
        except Exception as e:
            logging.error(f"Failed to send message to dead-letter topic: {e}")

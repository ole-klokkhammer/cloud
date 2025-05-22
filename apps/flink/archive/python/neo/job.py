from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema

def main():
    # Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()

    # Configure Kafka consumer
    kafka_consumer = FlinkKafkaConsumer(
        topics='my-kafka-topic',
        value_deserializer=SimpleStringSchema(),
        properties={
            'bootstrap.servers': 'kafka-broker:9092',
            'group.id': 'flink-consumer-group'
        }
    )

    # Add Kafka source to the environment
    stream = env.add_source(kafka_consumer)

    # Process the stream (e.g., print to console)
    stream.print()

    # Execute the job
    env.execute("Kafka Reader Job")

if __name__ == '__main__':
    main()
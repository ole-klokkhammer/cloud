package com.olklokk.flink.neo

import org.apache.flink.api.common.eventtime.WatermarkStrategy
import org.apache.flink.api.common.serialization.SimpleStringSchema
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment
import java.util.*

fun main() {
    val env = StreamExecutionEnvironment.getExecutionEnvironment()
    val kafkaBootstrapServer = "kafka-kafka-bootstrap.kafka:9092"
    val topic = "otlp_logs"


    val kafkaConsumer = KafkaSource.builder<String>()
        .setBootstrapServers(kafkaBootstrapServer)
        .setTopics(topic)
        .setStartingOffsets(OffsetsInitializer.earliest())
        .setValueOnlyDeserializer(SimpleStringSchema())
        .build()

    val kafkaStream = env.fromSource(
        kafkaConsumer,
        WatermarkStrategy.noWatermarks<String>(),
        "Kafka Source"
    )

    kafkaStream.print()

    // Execute the Flink job
    env.execute("Flink Kafka Consumer Example")
}
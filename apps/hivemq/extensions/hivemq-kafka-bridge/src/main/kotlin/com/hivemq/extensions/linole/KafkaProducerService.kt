package com.hivemq.extensions.linole

import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.ProducerConfig
import org.apache.kafka.clients.producer.ProducerRecord
import org.apache.kafka.common.serialization.ByteBufferSerializer
import org.apache.kafka.common.serialization.StringSerializer
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.nio.ByteBuffer
import java.util.*

class KafkaProducerService(
    bootstrapServers: String,
    private val topic: String
) {
    private val log: Logger = LoggerFactory.getLogger(KafkaProducerService::class.java)

    private val producer: KafkaProducer<String, ByteBuffer> = KafkaProducer(Properties().apply {
        put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers)
        put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer::class.java.name)
        put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, ByteBufferSerializer::class.java.name)
    })

    fun sendMessage(key: String, value: ByteBuffer, headers: Map<String, ByteArray?> = emptyMap()) {
        producer.send(ProducerRecord(topic, key, value).also {
            it.addHeaders(headers)
        })
    }

    fun ProducerRecord<String, ByteBuffer>.addHeaders(headers: Map<String, ByteArray?>) {
        try {
            headers.entries.forEach { newHeader ->
                headers().add(newHeader.key, newHeader.value)
            }
        } catch (exception: Exception) {
            log.error("Failed to add header", exception)
        }
    }

    fun close() {
        producer.close()
    }
}
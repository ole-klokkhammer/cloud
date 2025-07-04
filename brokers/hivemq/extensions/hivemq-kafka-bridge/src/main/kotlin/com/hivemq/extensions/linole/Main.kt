package com.hivemq.extensions.linole

import com.hivemq.extension.sdk.api.ExtensionMain
import com.hivemq.extension.sdk.api.annotations.NotNull
import com.hivemq.extension.sdk.api.events.EventRegistry
import com.hivemq.extension.sdk.api.parameter.*
import com.hivemq.extension.sdk.api.services.Services
import com.hivemq.extension.sdk.api.services.intializer.InitializerRegistry
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.nio.ByteBuffer
import kotlin.jvm.optionals.getOrDefault
import kotlin.jvm.optionals.getOrNull

class Main : ExtensionMain {

    private val log: Logger = LoggerFactory.getLogger(Main::class.java)
    private lateinit var kafkaProducerService: KafkaProducerService

    override fun extensionStart(
        extensionStartInput: @NotNull ExtensionStartInput, extensionStartOutput: @NotNull ExtensionStartOutput
    ) {
        try {
            kafkaProducerService = KafkaProducerService(
                topic = System.getenv("KAFKA_TOPIC") ?: "hivemq",
                bootstrapServers = System.getenv("KAFKA_BOOTSTRAP_SERVERS") ?: "kafka-kafka-bootstrap.kafka:9092"
            )

            Services.initializerRegistry().setClientInitializer { _, clientContext ->
                clientContext.addPublishInboundInterceptor { input, output ->
                    try {
                        kafkaProducerService.sendMessage(
                            input.publishPacket.topic,
                            input.publishPacket.payload.getOrNull()!!,
                            mapOf(
                                "clientId" to input.clientInformation.clientId.toByteArray(),
                                "contentType" to input.publishPacket.contentType.getOrNull()?.toByteArray(),
                                "payloadFormatIndicator" to input.publishPacket.payloadFormatIndicator.getOrNull()?.name?.toByteArray(),
                                "userProperties" to input.publishPacket.userProperties.asList().joinToString(",")
                                    .toByteArray()
                            )
                        )
                    } catch (exception: Exception) {
                        log.error("Exception thrown at publish", exception)
                    }
                }
            }

            val extensionInformation = extensionStartInput.extensionInformation
            log.info("Started {}:{}", extensionInformation.name, extensionInformation.version)
        } catch (e: Exception) {
            log.error("Exception thrown at extension start: ", e)
        }
    }

    override fun extensionStop(
        extensionStopInput: @NotNull ExtensionStopInput, extensionStopOutput: @NotNull ExtensionStopOutput
    ) {
        val extensionInformation = extensionStopInput.extensionInformation
        log.info("Stopped {}:{}", extensionInformation.name, extensionInformation.version)
    }
}
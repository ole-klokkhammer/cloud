package com.linole.services

import com.fasterxml.jackson.databind.ObjectMapper
import com.linole.common.coroutines.Dispatcher
import com.linole.common.logging.injectLogger
import com.linole.common.utils.safeFromJsonString
import com.linole.common.utils.safeToJsonString
import com.linole.mqtt.MqttMessage
import com.linole.mqtt.client.Mqtt3Client
import com.linole.services.model.EnvironmentalSensorData
import com.linole.services.model.MessageType
import com.linole.services.model.StatusCommand
import com.linole.utils.getEventType
import io.ktor.util.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.time.Instant
import kotlin.coroutines.CoroutineContext

class HotnCoolService(
    mqttClient: Mqtt3Client,
    jacksonMapper: ObjectMapper,
    dispatcher: Dispatcher,
    override val modelId: String = "527",
    override val deviceId: String,
) : DysonService(
    mqttClient, jacksonMapper, dispatcher
)

class HumidifierService(
    mqttClient: Mqtt3Client,
    jacksonMapper: ObjectMapper,
    dispatcher: Dispatcher,
    override val modelId: String = "358",
    override val deviceId: String,
) : DysonService(
    mqttClient, jacksonMapper, dispatcher
)

abstract class DysonService(
    private val mqttClient: Mqtt3Client,
    private val jacksonMapper: ObjectMapper,
    private val dispatcher: Dispatcher
) : CoroutineScope {
    override val coroutineContext: CoroutineContext = SupervisorJob() + Dispatchers.Default
    private val logger by injectLogger()
    private var statusRequestJob: Job? = null
    private var currentStatusSubJob: Job? = null
    private var faultsStatusSubJob: Job? = null
    private var softwareStatusSubJob: Job? = null
    private var connectionStatusSubJob: Job? = null

    private val environmentSensorStatus = MutableStateFlow<EnvironmentalSensorData?>(null)
    private val environmentStatus = MutableStateFlow<String?>(null)
    private val faultStatus = MutableStateFlow<String?>(null)
    private val softwareStatus = MutableStateFlow<String?>(null)
    private val connectionStatus = MutableStateFlow<String?>(null)

    protected abstract val modelId: String
    protected abstract val deviceId: String
    fun deviceId() = deviceId;

    fun environmentSensorStatusFlow() = environmentSensorStatus.asSharedFlow()
    fun environmentStatusFlow() = environmentStatus.asSharedFlow()
    fun faultStatusFlow() = faultStatus.asSharedFlow()
    fun softwareStatusFlow() = softwareStatus.asSharedFlow()
    fun connectionStatusFlow() = connectionStatus.asSharedFlow()

    fun start() = launch {
        mqttClient.connectionStateFlow().collect { isConnected ->
            if (isConnected) {
                statusRequestJob = startRequestingStatus()
                currentStatusSubJob = subscribeCurrentStatus()
                faultsStatusSubJob = subscribeFaults()
                softwareStatusSubJob = subscribeSoftware()
                connectionStatusSubJob = subscribeConnection()
            } else {
                statusRequestJob?.cancel()
                currentStatusSubJob?.cancel()
                faultsStatusSubJob?.cancel()
                softwareStatusSubJob?.cancel()
                connectionStatusSubJob?.cancel()
            }
        }
    }

    fun stop() {
        coroutineContext.cancel()
    }

    private fun baseTopic() = "$modelId/$deviceId"

    private fun startRequestingStatus() = launch(dispatcher.default()) {
        while (isActive) {
            val commandTopic = "${baseTopic()}/command"
            val jsonRequest = jacksonMapper.safeToJsonString(
                StatusCommand(
                    function = commandTopic,
                    modeReason = "LAPP",
                    time = Instant.now().toString(),
                    msg = "REQUEST-CURRENT-STATE"
                )
            )

            if (jsonRequest != null) {
                logger.debug("Requesting status $jsonRequest")
                mqttClient.runCatching { publish(commandTopic, jsonRequest.toByteArray()) }.onFailure {
                    logger.error(it)
                }
            }

            delay(60000) // 1 minute
        }
    }

    private fun subscribeCurrentStatus() = launch(dispatcher.default()) {
        mqttClient.subscribe("${baseTopic()}/status/current")
        mqttClient.onMessage("${baseTopic()}/status/current").collect { message: MqttMessage ->
            try {
                jacksonMapper
                    .getEventType(message.payloadString)
                    .takeIf { it == MessageType.ENVIRONMENTAL_CURRENT_SENSOR_DATA }
                    ?.let {
                        environmentSensorStatus.emit(
                            jacksonMapper.safeFromJsonString<EnvironmentalSensorData>(
                                message.payloadString
                            )
                        )
                    }
                environmentStatus.emit(message.payloadString)
            } catch (e: Throwable) {
                logger.error(e)
            }
        }
    }

    private fun subscribeFaults() = launch(dispatcher.default()) {
        mqttClient.subscribe("${baseTopic()}/status/faults")
        mqttClient.onMessage("${baseTopic()}/status/faults").collect { message: MqttMessage ->
            try {
                faultStatus.emit(message.payloadString)
            } catch (e: Throwable) {
                logger.error(e)
            }
        }
    }

    private fun subscribeSoftware() = launch(dispatcher.default()) {
        mqttClient.subscribe("${baseTopic()}/status/software")
        mqttClient.onMessage("${baseTopic()}/status/software").collect { message: MqttMessage ->
            try {
                softwareStatus.emit(message.payloadString)
            } catch (e: Throwable) {
                logger.error(e)
            }
        }
    }

    private fun subscribeConnection() = launch(dispatcher.default()) {
        mqttClient.subscribe("${baseTopic()}/status/connection")
        mqttClient.onMessage("${baseTopic()}/status/connection").collect { message: MqttMessage ->
            try {
                connectionStatus.emit(message.payloadString)
            } catch (e: Throwable) {
                logger.error(e)
            }
        }
    }
}
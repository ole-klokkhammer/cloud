package com.linole.services

import com.linole.common.logging.injectLogger
import com.linole.mqtt.client.Mqtt3Client
import com.linole.services.model.EnvironmentData
import io.ktor.util.*
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch
import kotlin.coroutines.CoroutineContext

class PushService(
    private val mqttClient: Mqtt3Client,
    private val humidifier: HumidifierService,
    private val hotncool: HotnCoolService
) : CoroutineScope {
    override val coroutineContext: CoroutineContext = SupervisorJob() + Dispatchers.Default
    private val logger by injectLogger()

    private var humidifierListener: Job? = null
    private var hotncoolListener: Job? = null

    fun start() = launch {
        mqttClient.connectionStateFlow().collect { isConnected ->
            if (isConnected) {
                listenToHumidifier()
                listenToHotnCool()
            } else {
                humidifierListener?.cancel()
                hotncoolListener?.cancel()
            }
        }
    }

    fun stop() {
        coroutineContext.cancel()
    }

    private fun listenToHumidifier() {
        humidifierListener = launch {
            launch(this@launch.coroutineContext) {
                humidifier.environmentSensorStatusFlow().collect {
                    publishEnvironmentData("dyson/${humidifier.deviceId()}", it?.data)
                }
            }
            launch(this@launch.coroutineContext) {
                humidifier.environmentStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${humidifier.deviceId()}/current", it1) }
                    }
                }
            }
            launch(this@launch.coroutineContext) {
                humidifier.faultStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${humidifier.deviceId()}/faults", it1) }
                    }
                }
            }
            launch(this@launch.coroutineContext) {
                humidifier.softwareStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${humidifier.deviceId()}/software", it1) }
                    }
                }
            }
            launch(this@launch.coroutineContext) {
                humidifier.connectionStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${humidifier.deviceId()}/connection", it1) }
                    }
                }
            }
        }
    }

    private fun listenToHotnCool() {
        hotncoolListener = launch {
            launch(this@launch.coroutineContext) {
                hotncool.environmentSensorStatusFlow().collect {
                    publishEnvironmentData("dyson/${hotncool.deviceId()}", it?.data)
                }
            }
            launch(this@launch.coroutineContext) {
                hotncool.environmentStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${hotncool.deviceId()}/current", it1) }
                    }
                }
            }
            launch(this@launch.coroutineContext) {
                hotncool.faultStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${hotncool.deviceId()}/faults", it1) }
                    }
                }
            }
            launch(this@launch.coroutineContext) {
                hotncool.softwareStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${hotncool.deviceId()}/software", it1) }
                    }
                }
            }
            launch(this@launch.coroutineContext) {
                hotncool.connectionStatusFlow().collect {
                    mqttClient.runCatching {
                        it?.toByteArray()
                            ?.let { it1 -> publish("dyson/${hotncool.deviceId()}/connection", it1) }
                    }
                }
            }
        }
    }

    private fun publishEnvironmentData(topic: String, data: Map<String, String>?) {
        try {
            data?.keys?.forEach { key ->
                mqttClient.runCatching {
                    publish(
                        "$topic/$key",
                        data.getValue(key).toByteArray()
                    )
                }
            }
        } catch (e: Throwable) {
            logger.error(e)
        }
    }
}
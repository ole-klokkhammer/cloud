package com.linole.services

import com.linole.common.Environment
import com.linole.common.Qualifiers.HotncoolMqttQualifier
import com.linole.common.Qualifiers.HumidifierMqttQualifier
import com.linole.common.Qualifiers.MainMqttQualifier
import com.linole.mqtt.client.Mqtt3Client
import io.ktor.application.*
import org.koin.dsl.module
import org.koin.ktor.ext.inject


val serviceModules = module {
    single {
        HotnCoolService(
            get(HotncoolMqttQualifier),
            get(),
            get(),
            modelId = get<Environment>().MQTT_DYSON_HOT_COOL_MODELID,
            deviceId = get<Environment>().MQTT_DYSON_HOT_COOL_USERNAME
        )
    }

    single {
        HumidifierService(
            get(HumidifierMqttQualifier),
            get(),
            get(),
            modelId = get<Environment>().MQTT_DYSON_HUMIDIFIER_MODELID,
            deviceId = get<Environment>().MQTT_DYSON_HUMIDIFIER_USERNAME
        )
    }

    single {
        PushService(get(MainMqttQualifier), get(), get())
    }
}

fun Application.configureServices() {
    val hotnCoolService by inject<HotnCoolService>()
    val humidifierService by inject<HumidifierService>()
    val pushService by inject<PushService>()
    val mainMqttClient by inject<Mqtt3Client>(MainMqttQualifier)
    val humidifierMqttClient by inject<Mqtt3Client>(HumidifierMqttQualifier)
    val hotnCoolMqttClient by inject<Mqtt3Client>(HotncoolMqttQualifier)

    environment.monitor.subscribe(ApplicationStarted) {
        mainMqttClient.connect()
        humidifierMqttClient.connect()
        hotnCoolMqttClient.connect()
        hotnCoolService.start()
        humidifierService.start()
        pushService.start()
    }
    environment.monitor.subscribe(ApplicationStopping) {
        pushService.stop()
        hotnCoolService.stop()
        humidifierService.stop()
        mainMqttClient.disconnect()
        humidifierMqttClient.disconnect()
        hotnCoolMqttClient.disconnect()
    }
}
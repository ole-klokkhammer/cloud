package com.linole.common

import com.fasterxml.jackson.databind.ObjectMapper
import com.linole.common.Qualifiers.HotncoolMqttQualifier
import com.linole.common.Qualifiers.HumidifierMqttQualifier
import com.linole.common.Qualifiers.MainMqttQualifier
import com.linole.common.coroutines.DefaultDispatcher
import com.linole.common.coroutines.Dispatcher
import com.linole.mqtt.MqttProperties
import com.linole.mqtt.TimeoutProperties
import com.linole.mqtt.client.Mqtt3Client
import io.ktor.application.*
import org.koin.core.qualifier.Qualifier
import org.koin.dsl.module

object Qualifiers {
    val MainMqttQualifier = object : Qualifier {
        override val value = "Main"
    }
    val HumidifierMqttQualifier = object : Qualifier {
        override val value = "Humidifier"
    }
    val HotncoolMqttQualifier = object : Qualifier {
        override val value = "HotnCool"
    }
}

fun Application.commonModules() = module {
    single { log }
    single { ObjectMapper() }
    single<Dispatcher> { DefaultDispatcher() }

    single {
        fun getProp(prop: String): String? {
            return environment.config.propertyOrNull(prop)?.getString()?.trim()
        }
        return@single Environment(
            MQTT_MAIN_CLIENTID = getProp("mqtt.main.clientId") ?: "dyson2mqtt",
            MQTT_MAIN_HOST = getProp("mqtt.main.host") ?: "mqttbroker",
            MQTT_MAIN_PORT = getProp("mqtt.main.port")?.toInt() ?: 1883,
            MQTT_MAIN_USERNAME = getProp("mqtt.main.username"),
            MQTT_MAIN_PASSWORD = getProp("mqtt.main.password"),
            MQTT_MAIN_KEEPALIVE = 60,
            MQTT_MAIN_TIMEOUT = object : TimeoutProperties {
                override val connect: Long = 10000L
                override val disconnect: Long = 10000L
                override val publish: Long = 10000L
                override val subscribe: Long = 10000L
                override val unsubscribe: Long = 10000L
            },

            MQTT_DYSON_HUMIDIFIER_CLIENTID = getProp("mqtt.dyson_humidifier.clientId") ?: "dyson2mqtt",
            MQTT_DYSON_HUMIDIFIER_HOST = getProp("mqtt.dyson_humidifier.host") ?: "mqttbroker",
            MQTT_DYSON_HUMIDIFIER_PORT = getProp("mqtt.dyson_humidifier.port")?.toInt() ?: 1883,
            MQTT_DYSON_HUMIDIFIER_MODELID = getProp("mqtt.dyson_humidifier.modelId") ?: "",
            MQTT_DYSON_HUMIDIFIER_USERNAME = getProp("mqtt.dyson_humidifier.username") ?: "",
            MQTT_DYSON_HUMIDIFIER_PASSWORD = getProp("mqtt.dyson_humidifier.password") ?: "",
            MQTT_DYSON_HUMIDIFIER_KEEPALIVE = 60,
            MQTT_DYSON_HUMIDIFIER_TIMEOUT = object : TimeoutProperties {
                override val connect: Long = 10000L
                override val disconnect: Long = 10000L
                override val publish: Long = 10000L
                override val subscribe: Long = 10000L
                override val unsubscribe: Long = 10000L
            },
            MQTT_DYSON_HOT_COOL_CLIENTID = getProp("mqtt.dyson_hot_cool.clientId") ?: "dyson2mqtt",
            MQTT_DYSON_HOT_COOL_HOST = getProp("mqtt.dyson_hot_cool.host") ?: "mqttbroker",
            MQTT_DYSON_HOT_COOL_PORT = getProp("mqtt.dyson_hot_cool.port")?.toInt() ?: 1883,
            MQTT_DYSON_HOT_COOL_MODELID = getProp("mqtt.dyson_hot_cool.modelId") ?: "",
            MQTT_DYSON_HOT_COOL_USERNAME = getProp("mqtt.dyson_hot_cool.username") ?: "",
            MQTT_DYSON_HOT_COOL_PASSWORD = getProp("mqtt.dyson_hot_cool.password") ?: "",
            MQTT_DYSON_HOT_COOL_KEEPALIVE = 60,
            MQTT_DYSON_HOT_COOL_TIMEOUT = object : TimeoutProperties {
                override val connect: Long = 10000L
                override val disconnect: Long = 10000L
                override val publish: Long = 10000L
                override val subscribe: Long = 10000L
                override val unsubscribe: Long = 10000L
            }
        )
    }

    single(MainMqttQualifier) {
        Mqtt3Client(object : MqttProperties {
            override val clientId: String = get<Environment>().MQTT_MAIN_CLIENTID
            override val host: String = get<Environment>().MQTT_MAIN_HOST
            override val port: Int = get<Environment>().MQTT_MAIN_PORT
            override val keepAlive: Int = get<Environment>().MQTT_MAIN_KEEPALIVE
            override val username: String? = get<Environment>().MQTT_MAIN_USERNAME
            override val password: String? = get<Environment>().MQTT_MAIN_PASSWORD
            override val timeout: TimeoutProperties = get<Environment>().MQTT_MAIN_TIMEOUT
        }, get())
    }

    single(HumidifierMqttQualifier) {
        Mqtt3Client(object : MqttProperties {
            override val clientId: String = get<Environment>().MQTT_DYSON_HUMIDIFIER_CLIENTID
            override val host: String = get<Environment>().MQTT_DYSON_HUMIDIFIER_HOST
            override val port: Int = get<Environment>().MQTT_DYSON_HUMIDIFIER_PORT
            override val keepAlive: Int = get<Environment>().MQTT_DYSON_HUMIDIFIER_KEEPALIVE
            override val username: String = get<Environment>().MQTT_DYSON_HUMIDIFIER_USERNAME
            override val password: String = get<Environment>().MQTT_DYSON_HUMIDIFIER_PASSWORD
            override val timeout: TimeoutProperties = get<Environment>().MQTT_DYSON_HUMIDIFIER_TIMEOUT
        }, get())
    }

    single(HotncoolMqttQualifier) {
        Mqtt3Client(object : MqttProperties {
            override val clientId: String = get<Environment>().MQTT_DYSON_HOT_COOL_CLIENTID
            override val host: String = get<Environment>().MQTT_DYSON_HOT_COOL_HOST
            override val port: Int = get<Environment>().MQTT_DYSON_HOT_COOL_PORT
            override val keepAlive: Int = get<Environment>().MQTT_DYSON_HOT_COOL_KEEPALIVE
            override val username: String = get<Environment>().MQTT_DYSON_HOT_COOL_USERNAME
            override val password: String = get<Environment>().MQTT_DYSON_HOT_COOL_PASSWORD
            override val timeout: TimeoutProperties = get<Environment>().MQTT_DYSON_HOT_COOL_TIMEOUT
        }, get())
    }
}
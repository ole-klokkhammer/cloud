package com.linole.common

import com.linole.mqtt.TimeoutProperties

data class Environment(
    val MQTT_MAIN_CLIENTID: String,
    val MQTT_MAIN_HOST: String,
    val MQTT_MAIN_PORT: Int,
    val MQTT_MAIN_USERNAME: String?,
    val MQTT_MAIN_PASSWORD: String?,
    val MQTT_MAIN_KEEPALIVE: Int,
    val MQTT_MAIN_TIMEOUT: TimeoutProperties,

    val MQTT_DYSON_HUMIDIFIER_CLIENTID: String,
    val MQTT_DYSON_HUMIDIFIER_HOST: String,
    val MQTT_DYSON_HUMIDIFIER_PORT: Int,
    val MQTT_DYSON_HUMIDIFIER_MODELID: String,
    val MQTT_DYSON_HUMIDIFIER_USERNAME: String,
    val MQTT_DYSON_HUMIDIFIER_PASSWORD: String,
    val MQTT_DYSON_HUMIDIFIER_KEEPALIVE: Int,
    val MQTT_DYSON_HUMIDIFIER_TIMEOUT: TimeoutProperties,

    val MQTT_DYSON_HOT_COOL_CLIENTID: String,
    val MQTT_DYSON_HOT_COOL_HOST: String,
    val MQTT_DYSON_HOT_COOL_PORT: Int,
    val MQTT_DYSON_HOT_COOL_MODELID: String,
    val MQTT_DYSON_HOT_COOL_USERNAME: String,
    val MQTT_DYSON_HOT_COOL_PASSWORD: String,
    val MQTT_DYSON_HOT_COOL_KEEPALIVE: Int,
    val MQTT_DYSON_HOT_COOL_TIMEOUT: TimeoutProperties,
)
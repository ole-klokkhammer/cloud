package com.linole.services.model

import com.fasterxml.jackson.annotation.JsonFormat
import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonValue


data class StatusCommand(
    @JsonProperty("f")
    val function: String,

    @JsonProperty("mode-reason")
    val modeReason: String,

    @JsonProperty("time")
    val time: String,

    @JsonProperty("msg")
    val msg: String,
)

@JsonIgnoreProperties(ignoreUnknown = true)
enum class MessageType(val value: String) {
    CURRENT_STATE("CURRENT-STATE"),
    STATE_CHANGE("STATE-CHANGE"),
    ENVIRONMENTAL_CURRENT_SENSOR_DATA("ENVIRONMENTAL-CURRENT-SENSOR-DATA");

    @JsonValue
    open fun value(): String = value
}

@JsonIgnoreProperties(ignoreUnknown = true)
data class EventType(
    @JsonProperty("msg")
    @JsonFormat(shape = JsonFormat.Shape.OBJECT)
    val type: MessageType
)

@JsonIgnoreProperties(ignoreUnknown = true)
data class EnvironmentalSensorData(
    @JsonProperty("msg")
    @JsonFormat(shape = JsonFormat.Shape.OBJECT)
    val msg: MessageType,

    @JsonProperty("data")
    val data: Map<String, String>?
)

data class EnvironmentData(
    @JsonProperty("tact")
    val tact: String,

    @JsonProperty("hact")
    val hact: String,

    @JsonProperty("pm25")
    val pm25: String,

    @JsonProperty("pm10")
    val pm10: String,

    @JsonProperty("va10")
    val va10: String,

    @JsonProperty("noxl")
    val noxl: String,

    @JsonProperty("p25r")
    val p25r: String,

    @JsonProperty("p10r")
    val p10r: String,

    @JsonProperty("sltm")
    val sltm: String,
)

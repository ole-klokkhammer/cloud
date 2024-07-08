package com.linole.common.utils

import com.fasterxml.jackson.core.JsonParseException
import com.fasterxml.jackson.core.JsonProcessingException
import com.fasterxml.jackson.databind.JsonMappingException
import com.fasterxml.jackson.databind.ObjectMapper
import kotlinx.coroutines.runBlocking

@Throws(JsonProcessingException::class)
fun <T> ObjectMapper.toJsonString(value: T): String? = runBlocking {
    return@runBlocking writeValueAsString(value)
}

@Throws(JsonParseException::class, JsonProcessingException::class, JsonMappingException::class)
inline fun <reified T> ObjectMapper.fromJsonString(value: String): T? = runBlocking {
    return@runBlocking readValue(value, T::class.java)
}

fun <T> ObjectMapper.safeToJsonString(value: T): String? = try {
    toJsonString(value)
} catch (e: Throwable) {
    null
}

inline fun <reified T> ObjectMapper.safeFromJsonString(value: String): T? = try {
    fromJsonString(value)
} catch (e: Throwable) {
    null
}

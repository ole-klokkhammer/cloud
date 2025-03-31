package com.linole.utils

import com.fasterxml.jackson.databind.ObjectMapper
import com.linole.common.utils.safeFromJsonString
import com.linole.services.model.EventType

fun ObjectMapper.getEventType(payloadString: String) = safeFromJsonString<EventType>(payloadString)?.type

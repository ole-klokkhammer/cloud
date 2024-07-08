package com.linole

import com.linole.common.commonModules
import com.linole.services.configureServices
import com.linole.services.serviceModules
import io.ktor.application.*
import org.koin.ktor.ext.Koin

fun main(args: Array<String>): Unit = io.ktor.server.netty.EngineMain.main(args)

@Suppress("unused")
fun Application.module() {
    install(Koin) {
        modules(commonModules(), serviceModules)
    }
    configureServices()
}

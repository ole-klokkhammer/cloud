package com.linole.common.coroutines

import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers

interface Dispatcher {
    fun default(): CoroutineDispatcher
    fun io(): CoroutineDispatcher
}

class DefaultDispatcher : Dispatcher {
    override fun default(): CoroutineDispatcher = Dispatchers.Default
    override fun io(): CoroutineDispatcher = Dispatchers.IO
}
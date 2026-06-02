open class EventHandler(val handlerName: String) {
    var eventsHandled: Int = 0

    open fun handle(event: Event) {
        eventsHandled++
        println("  [$handlerName] handled: ${event.describe()}")
    }
}

class LoggingHandler(name: String) : EventHandler(name) {
    val messages = mutableListOf<String>()

    override fun handle(event: Event) {
        eventsHandled++
        val msg = "LOG: ${event.describe()}"
        messages.add(msg)
        println("  [$handlerName] $msg")
    }

    fun printMessages() {
        println("$handlerName logged ${messages.size} messages:")
        for (m in messages) {
            println("  $m")
        }
    }
}

class CountingHandler(name: String) : EventHandler(name) {
    val countKeys = mutableListOf<String>()
    val countValues = mutableListOf<Int>()

    override fun handle(event: Event) {
        eventsHandled++
        var found = false
        for (i in 0 until countKeys.size) {
            if (countKeys[i] == event.source) {
                countValues[i] = countValues[i] + 1
                found = true
                break
            }
        }
        if (!found) {
            countKeys.add(event.source)
            countValues.add(1)
        }
        println("  [$handlerName] counted event from ${event.source}")
    }

    fun printCounts() {
        println("$handlerName counts:")
        for (i in 0 until countKeys.size) {
            println("  ${countKeys[i]}: ${countValues[i]} events")
        }
    }
}

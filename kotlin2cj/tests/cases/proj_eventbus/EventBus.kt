class EventBus(val busName: String) {
    val handlerTypes = mutableListOf<String>()
    val handlerLists = mutableListOf<MutableList<EventHandler>>()
    val log = EventLog()

    fun findHandlers(eventType: String): MutableList<EventHandler>? {
        for (i in 0 until handlerTypes.size) {
            if (handlerTypes[i] == eventType) {
                return handlerLists[i]
            }
        }
        return null
    }

    fun register(eventType: String, handler: EventHandler) {
        val list = findHandlers(eventType)
        if (list != null) {
            list.add(handler)
        } else {
            val newList = mutableListOf<EventHandler>()
            newList.add(handler)
            handlerTypes.add(eventType)
            handlerLists.add(newList)
        }
        println("Registered handler '${handler.handlerName}' for '$eventType'")
    }

    fun emit(event: Event) {
        log.record(event)
        val list = findHandlers(event.eventType)
        if (list != null) {
            for (h in list) {
                h.handle(event)
            }
        } else {
            println("No handlers for event type '${event.eventType}'")
        }
    }

    fun printStats() {
        println("=== EventBus '$busName' Stats ===")
        println("Total events: ${log.entries.size}")
        val types = mutableListOf<String>()
        for (e in log.entries) {
            var found = false
            for (t in types) {
                if (t == e.eventType) {
                    found = true
                    break
                }
            }
            if (!found) {
                types.add(e.eventType)
            }
        }
        for (t in types) {
            println("  $t: ${log.countByType(t)} events")
        }
    }
}

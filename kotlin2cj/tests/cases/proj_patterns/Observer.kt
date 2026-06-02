data class Event(
    val type: String,
    val source: String,
    val payload: String,
    val priority: Int = 0
)

interface EventListener {
    val listenerName: String
    fun onEvent(event: Event): String
}

abstract class BaseEventListener(override val listenerName: String) : EventListener {
    val history = ArrayList<String>()
    var handledCount = 0

    fun remember(message: String): String {
        handledCount += 1
        history.add(message)
        return message
    }

    fun lastMessage(): String {
        return if (history.size == 0) {
            "<none>"
        } else {
            history[history.size - 1]
        }
    }

    fun describeHistory(): String {
        return history.joinToString(" || ")
    }
}

class LoggingListener(name: String, val channel: String) : BaseEventListener(name) {
    override fun onEvent(event: Event): String {
        val message = "[$channel] $listenerName logged ${event.type} from ${event.source} payload=${event.payload} priority=${event.priority}"
        return remember(message)
    }
}

class CountingListener(name: String) : BaseEventListener(name) {
    val typeCounts = HashMap<String, Int>()
    val sourceCounts = HashMap<String, Int>()

    override fun onEvent(event: Event): String {
        val currentType = typeCounts[event.type] ?: 0
        typeCounts[event.type] = currentType + 1
        val currentSource = sourceCounts[event.source] ?: 0
        sourceCounts[event.source] = currentSource + 1
        val message = "$listenerName counted ${event.type} for ${event.source} -> type=${typeCounts[event.type]} source=${sourceCounts[event.source]}"
        return remember(message)
    }

    fun typeSummary(): String {
        val keys = ArrayList<String>()
        for (key in typeCounts.keys) {
            keys.add(key)
        }
        val ordered = keys.sorted()
        val parts = ArrayList<String>()
        for (key in ordered) {
            parts.add("$key=${typeCounts[key] ?: 0}")
        }
        return parts.joinToString(", ")
    }

    fun sourceSummary(): String {
        val keys = ArrayList<String>()
        for (key in sourceCounts.keys) {
            keys.add(key)
        }
        val ordered = keys.sorted()
        val parts = ArrayList<String>()
        for (key in ordered) {
            parts.add("$key=${sourceCounts[key] ?: 0}")
        }
        return parts.joinToString(", ")
    }
}

class FilteringListener(
    name: String,
    val allowedType: String,
    val sink: MutableList<String>
) : BaseEventListener(name) {
    override fun onEvent(event: Event): String {
        val accepted = event.type == allowedType
        val message = if (accepted) {
            "$listenerName accepted ${event.type} from ${event.source}"
        } else {
            "$listenerName ignored ${event.type} from ${event.source}"
        }
        if (accepted) {
            sink.add("accepted:${event.source}:${event.payload}")
        }
        return remember(message)
    }
}

class AuditListener(name: String) : BaseEventListener(name) {
    override fun onEvent(event: Event): String {
        val normalized = event.payload.trim().manualUpper().replace(" ", "_")
        val message = "$listenerName audit ${event.type}:${event.source}:$normalized"
        return remember(message)
    }
}

class EventBus(val busName: String) {
    private val topics = ArrayList<String>()
    private val listeners = ArrayList<ArrayList<EventListener>>()
    val publishLog = ArrayList<String>()

    private fun topicIndex(topic: String): Int {
        var i = 0
        while (i < topics.size) {
            if (topics[i] == topic) {
                return i
            }
            i += 1
        }
        return -1
    }

    fun subscribe(topic: String, listener: EventListener) {
        val index = topicIndex(topic)
        if (index >= 0) {
            listeners[index].add(listener)
        } else {
            topics.add(topic)
            val bucket = ArrayList<EventListener>()
            bucket.add(listener)
            listeners.add(bucket)
        }
    }

    fun unsubscribe(topic: String, listenerName: String): Boolean {
        val index = topicIndex(topic)
        if (index < 0) {
            return false
        }
        val bucket = listeners[index]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i].listenerName == listenerName) {
                bucket.removeAt(i)
                return true
            }
            i += 1
        }
        return false
    }

    fun publish(event: Event): MutableList<String> {
        val messages = mutableListOf<String>()
        publishLog.add("${event.type}@${event.source}:${event.payload}:${event.priority}")
        val index = topicIndex(event.type)
        if (index < 0) {
            messages.add("EventBus[$busName] no listeners for ${event.type}")
            return messages
        }
        val bucket = listeners[index]
        if (bucket.size == 0) {
            messages.add("EventBus[$busName] no listeners for ${event.type}")
            return messages
        }
        for (listener in bucket) {
            messages.add(listener.onEvent(event))
        }
        return messages
    }

    fun listenerCount(topic: String): Int {
        val index = topicIndex(topic)
        return if (index < 0) 0 else listeners[index].size
    }

    fun topicNames(): MutableList<String> {
        val copy = mutableListOf<String>()
        for (topic in topics) {
            copy.add(topic)
        }
        return copy
    }

    fun describeSubscriptions(): MutableList<String> {
        val lines = mutableListOf<String>()
        var i = 0
        while (i < topics.size) {
            val names = mutableListOf<String>()
            for (listener in listeners[i]) {
                names.add(listener.listenerName)
            }
            val joinedNames = names.joinToString(", ")
            lines.add("${topics[i]} -> $joinedNames")
            i += 1
        }
        return lines
    }

    fun publishSummary(): String {
        return publishLog.joinToString(" | ")
    }
}

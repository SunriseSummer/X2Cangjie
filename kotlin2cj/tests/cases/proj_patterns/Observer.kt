interface Observer {
    fun onEvent(event: String)
    fun observerName(): String
}

class EventBus {
    private val listeners = ArrayList<Observer>()

    fun subscribe(observer: Observer) {
        listeners.add(observer)
    }

    fun publish(event: String) {
        for (listener in listeners) {
            listener.onEvent(event)
        }
    }

    fun subscriberCount(): Int {
        return listeners.size
    }
}

class LogObserver(val name: String) : Observer {
    val logs = ArrayList<String>()

    override fun onEvent(event: String) {
        logs.add("[$name] received: $event")
    }

    override fun observerName(): String = name

    override fun toString(): String {
        val builder = StringBuilder()
        for (log in logs) {
            builder.append(log)
            builder.append("\n")
        }
        return builder.toString().trim()
    }
}

class FilterObserver(val name: String, val keyword: String) : Observer {
    val logs = ArrayList<String>()

    override fun onEvent(event: String) {
        if (event.contains(keyword)) {
            logs.add("[$name] matched '$keyword' in: $event")
        }
    }

    override fun observerName(): String = name
}

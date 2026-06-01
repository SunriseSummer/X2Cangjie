class Event(val eventType: String, val source: String, val data: String) {
    fun describe(): String = "[$eventType] from $source: $data"
}

class EventLog {
    val entries = mutableListOf<Event>()

    fun record(event: Event) {
        entries.add(event)
    }

    fun printLog() {
        println("=== Event Log (${entries.size} events) ===")
        for (e in entries) {
            println("  ${e.describe()}")
        }
    }

    fun countByType(eventType: String): Int {
        var count = 0
        for (e in entries) {
            if (e.eventType == eventType) count++
        }
        return count
    }
}

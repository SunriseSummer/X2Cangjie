// Event-driven simulation: simple discrete event simulator
data class Event(val time: Int, val name: String, val priority: Int)

class EventQueue {
    private val events = ArrayList<Event>()

    fun schedule(e: Event) {
        events.add(e)
        // Keep sorted by time, then by priority (higher first)
        for (i in events.size - 1 downTo 1) {
            if (events[i].time < events[i - 1].time ||
                (events[i].time == events[i - 1].time && events[i].priority > events[i - 1].priority)) {
                val tmp = events[i]
                events[i] = events[i - 1]
                events[i - 1] = tmp
            } else {
                break
            }
        }
    }

    fun next(): Event {
        val e = events[0]
        events.removeAt(0)
        return e
    }

    fun isEmpty(): Boolean = events.isEmpty()
    fun size(): Int = events.size
}

fun simulate(): ArrayList<String> {
    val eq = EventQueue()
    eq.schedule(Event(10, "process_A", 1))
    eq.schedule(Event(5, "process_B", 2))
    eq.schedule(Event(5, "process_C", 1))
    eq.schedule(Event(15, "process_D", 3))
    eq.schedule(Event(10, "process_E", 2))

    val log = ArrayList<String>()
    while (!eq.isEmpty()) {
        val e = eq.next()
        log.add("t=${e.time}: ${e.name} (p=${e.priority})")
    }
    return log
}

fun main() {
    val log = simulate()
    for (entry in log) {
        println(entry)
    }

    // Priority queue behavior
    val pq = EventQueue()
    pq.schedule(Event(1, "low", 1))
    pq.schedule(Event(1, "high", 10))
    pq.schedule(Event(1, "mid", 5))
    println("---")
    while (!pq.isEmpty()) {
        val e = pq.next()
        println("${e.name}: priority=${e.priority}")
    }
}

import std.collection.*

class Event <: ToString {
    let time: Int64
    let name: String
    let priority: Int64
    init(time: Int64, name: String, priority: Int64) {
        this.time = time
        this.name = name
        this.priority = priority
    }
    public func toString(): String {
        return "Event(time=${this.time}, name=${this.name}, priority=${this.priority})"
    }
}

class EventQueue {
    let events = ArrayList<Event>()
    func schedule(e: Event) {
        events.add(e)
        for (i in (events.size - 1)..=1 : -1) {
            if ((events[i].time < events[i - 1].time) || ((events[i].time == events[i - 1].time) && (events[i].priority > events[i - 1].priority))) {
                let tmp = events[i]
                events[i] = events[i - 1]
                events[i - 1] = tmp
            } else {
                break
            }
        }
    }
    func next(): Event {
        let e = events[0]
        events.remove(at: 0)
        return e
    }
    func isEmpty(): Bool {
        return events.isEmpty()
    }
    func size(): Int64 {
        return events.size
    }
}

func simulate(): ArrayList<String> {
    let eq = EventQueue()
    eq.schedule(Event(10, "process_A", 1))
    eq.schedule(Event(5, "process_B", 2))
    eq.schedule(Event(5, "process_C", 1))
    eq.schedule(Event(15, "process_D", 3))
    eq.schedule(Event(10, "process_E", 2))
    let log = ArrayList<String>()
    while (!eq.isEmpty()) {
        let e = eq.next()
        log.add("t=${e.time}: ${e.name} (p=${e.priority})")
    }
    return log
}

main() {
    let log = simulate()
    for (entry in log) {
        println(entry)
    }
    let pq = EventQueue()
    pq.schedule(Event(1, "low", 1))
    pq.schedule(Event(1, "high", 10))
    pq.schedule(Event(1, "mid", 5))
    println("---")
    while (!pq.isEmpty()) {
        let e = pq.next()
        println("${e.name}: priority=${e.priority}")
    }
}

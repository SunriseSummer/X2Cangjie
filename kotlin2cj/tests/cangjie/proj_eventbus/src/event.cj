package proj_eventbus

import std.collection.*

class Event {
    let eventType: String
    let source: String
    let data: String
    init(eventType: String, source: String, data: String) {
        this.eventType = eventType
        this.source = source
        this.data = data
    }
    func describe(): String {
        return "[${eventType}] from ${source}: ${data}"
    }
}

class EventLog {
    let entries = ArrayList<Event>()
    func record(event: Event) {
        entries.add(event)
    }
    func printLog() {
        println("=== Event Log (${entries.size} events) ===")
        for (e in entries) {
            println("  ${e.describe()}")
        }
    }
    func countByType(eventType: String): Int64 {
        var count = 0
        for (e in entries) {
            if (e.eventType == eventType) {
                count += 1
            }
        }
        return count
    }
}

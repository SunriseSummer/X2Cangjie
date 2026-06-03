package proj_eventbus

import std.collection.*

class EventBus {
    let busName: String
    init(busName: String) {
        this.busName = busName
    }
    let handlerTypes = ArrayList<String>()
    let handlerLists = ArrayList<ArrayList<EventHandler>>()
    let log = EventLog()
    func findHandlers(eventType: String): ?ArrayList<EventHandler> {
        for (i in 0..handlerTypes.size) {
            if (handlerTypes[i] == eventType) {
                return handlerLists[i]
            }
        }
        return None
    }
    func register(eventType: String, handler: EventHandler) {
        let list = findHandlers(eventType)
        if (let Some(list) <- list) {
            list.add(handler)
        } else {
            let newList = ArrayList<EventHandler>()
            newList.add(handler)
            handlerTypes.add(eventType)
            handlerLists.add(newList)
        }
        println("Registered handler '${handler.handlerName}' for '${eventType}'")
    }
    func emit(event: Event) {
        log.record(event)
        let list = findHandlers(event.eventType)
        if (let Some(list) <- list) {
            for (h in list) {
                h.handle(event)
            }
        } else {
            println("No handlers for event type '${event.eventType}'")
        }
    }
    func printStats() {
        println("=== EventBus '${busName}' Stats ===")
        println("Total events: ${log.entries.size}")
        let types = ArrayList<String>()
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
            println("  ${t}: ${log.countByType(t)} events")
        }
    }
}

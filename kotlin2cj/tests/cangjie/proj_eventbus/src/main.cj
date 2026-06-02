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

open class EventHandler {
    let handlerName: String
    init(handlerName: String) {
        this.handlerName = handlerName
    }
    var eventsHandled: Int64 = 0
    public open func handle(event: Event) {
        eventsHandled += 1
        println("  [${handlerName}] handled: ${event.describe()}")
    }
}

class LoggingHandler <: EventHandler {
    init(name: String) {
        super(name)
    }
    let messages = ArrayList<String>()
    public override func handle(event: Event) {
        eventsHandled += 1
        let msg = "LOG: ${event.describe()}"
        messages.add(msg)
        println("  [${handlerName}] ${msg}")
    }
    func printMessages() {
        println("${handlerName} logged ${messages.size} messages:")
        for (m in messages) {
            println("  ${m}")
        }
    }
}

class CountingHandler <: EventHandler {
    init(name: String) {
        super(name)
    }
    let countKeys = ArrayList<String>()
    let countValues = ArrayList<Int64>()
    public override func handle(event: Event) {
        eventsHandled += 1
        var found = false
        for (i in 0..countKeys.size) {
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
        println("  [${handlerName}] counted event from ${event.source}")
    }
    func printCounts() {
        println("${handlerName} counts:")
        for (i in 0..countKeys.size) {
            println("  ${countKeys[i]}: ${countValues[i]} events")
        }
    }
}

main() {
    let bus = EventBus("main")
    let logger = LoggingHandler("FileLogger")
    let counter = CountingHandler("Analytics")
    let generic = EventHandler("Notifier")
    bus.register("click", logger)
    bus.register("click", counter)
    bus.register("error", logger)
    bus.register("error", generic)
    bus.register("login", counter)
    println()
    bus.emit(Event("click", "button1", "pressed"))
    bus.emit(Event("click", "button2", "pressed"))
    bus.emit(Event("error", "server", "timeout"))
    bus.emit(Event("login", "user1", "success"))
    bus.emit(Event("login", "user2", "success"))
    bus.emit(Event("click", "button1", "double-click"))
    bus.emit(Event("unknown", "system", "test"))
    println()
    bus.printStats()
    println()
    logger.printMessages()
    println()
    counter.printCounts()
    println()
    println("Logger handled: ${logger.eventsHandled}")
    println("Counter handled: ${counter.eventsHandled}")
    println("Notifier handled: ${generic.eventsHandled}")
}
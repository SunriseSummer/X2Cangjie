package proj_eventbus

import std.collection.*

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

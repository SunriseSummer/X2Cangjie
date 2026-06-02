package proj_eventbus

import std.collection.*

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

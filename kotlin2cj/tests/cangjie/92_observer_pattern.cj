import std.collection.*

abstract class Event {
    let name: String
    init(name: String) {
        this.name = name
    }
}

class ClickEvent <: Event {
    let x: Int64
    let y: Int64
    init(x: Int64, y: Int64) {
        super("click")
        this.x = x
        this.y = y
    }
}

class KeyEvent <: Event {
    let key: String
    init(key: String) {
        super("key")
        this.key = key
    }
}

abstract class Observer {
    public func onEvent(e: Event): Unit
}

class Logger <: Observer {
    let log = ArrayList<String>()
    public override func onEvent(e: Event) {
        match (e) {
            case e: ClickEvent => log.add("Click at (${e.x}, ${e.y})")
            case e: KeyEvent => log.add("Key: ${e.key}")
            case _ => throw Exception("")}
    }
    func dump() {
        for (entry in log) {
            println("  ${entry}")
        }
    }
}

class Counter <: Observer {
    var clicks = 0
    var keys = 0
    public override func onEvent(e: Event) {
        match (e) {
            case e: ClickEvent => clicks += 1
            case e: KeyEvent => keys += 1
            case _ => throw Exception("")}
    }
    func report() {
        println("  Clicks: ${clicks}, Keys: ${keys}")
    }
}

class EventBus {
    let observers = ArrayList<Observer>()
    func subscribe(o: Observer) {
        observers.add(o)
    }
    func emit(e: Event) {
        for (o in observers) {
            o.onEvent(e)
        }
    }
}

main() {
    let bus = EventBus()
    let logger = Logger()
    let counter = Counter()
    bus.subscribe(logger)
    bus.subscribe(counter)
    bus.emit(ClickEvent(10, 20))
    bus.emit(KeyEvent("Enter"))
    bus.emit(ClickEvent(30, 40))
    bus.emit(KeyEvent("Escape"))
    bus.emit(ClickEvent(50, 60))
    println("Logger:")
    logger.dump()
    println("Counter:")
    counter.report()
    println("Total events: ${logger.log.size}")
}

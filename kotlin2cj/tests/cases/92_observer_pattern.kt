// Observer pattern with interfaces and callbacks
abstract class Event(val name: String)

class ClickEvent(val x: Int, val y: Int) : Event("click")
class KeyEvent(val key: String) : Event("key")

abstract class Observer {
    abstract fun onEvent(e: Event)
}

class Logger : Observer() {
    val log = ArrayList<String>()
    override fun onEvent(e: Event) {
        when (e) {
            is ClickEvent -> log.add("Click at (${e.x}, ${e.y})")
            is KeyEvent -> log.add("Key: ${e.key}")
        }
    }
    fun dump() {
        for (entry in log) {
            println("  $entry")
        }
    }
}

class Counter : Observer() {
    var clicks = 0
    var keys = 0
    override fun onEvent(e: Event) {
        when (e) {
            is ClickEvent -> clicks++
            is KeyEvent -> keys++
        }
    }
    fun report() {
        println("  Clicks: $clicks, Keys: $keys")
    }
}

class EventBus {
    val observers = ArrayList<Observer>()
    fun subscribe(o: Observer) { observers.add(o) }
    fun emit(e: Event) {
        for (o in observers) {
            o.onEvent(e)
        }
    }
}

fun main() {
    val bus = EventBus()
    val logger = Logger()
    val counter = Counter()
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

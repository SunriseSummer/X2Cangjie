fun printSection(title: String) {
    println("=== $title ===")
}

fun main() {
    // Observer pattern
    printSection("Observer")
    val bus = EventBus()
    val logAll = LogObserver("AllLogger")
    val errorFilter = FilterObserver("ErrorFilter", "error")
    bus.subscribe(logAll)
    bus.subscribe(errorFilter)
    bus.publish("User logged in")
    bus.publish("File not found error")
    bus.publish("Data saved")
    bus.publish("Connection error occurred")
    println("Subscribers: ${bus.subscriberCount()}")
    println("All logs:")
    println(logAll)
    println("Error filter matches: ${errorFilter.logs.size}")
    for (log in errorFilter.logs) {
        println("  $log")
    }

    // Strategy pattern
    printSection("Strategy")
    val calc = Calculator()
    println("Strategy: ${calc.currentStrategy()}")
    println("10 + 5 = ${calc.calculate(10, 5)}")
    calc.setStrategy(SubtractStrategy())
    println("Strategy: ${calc.currentStrategy()}")
    println("10 - 5 = ${calc.calculate(10, 5)}")
    calc.setStrategy(MultiplyStrategy())
    println("Strategy: ${calc.currentStrategy()}")
    println("10 * 5 = ${calc.calculate(10, 5)}")

    // Command pattern
    printSection("Command")
    val doc = TextDocument()
    println(doc.applyCommand(AppendCommand(doc, "Hello")))
    println("Text: '${doc.text}'")
    println(doc.applyCommand(AppendCommand(doc, " World")))
    println("Text: '${doc.text}'")
    println(doc.applyCommand(AppendCommand(doc, "!")))
    println("Text: '${doc.text}'")
    println("History: ${doc.historyLog()}")
    println(doc.undoLast())
    println("Text after undo: '${doc.text}'")
    println(doc.undoLast())
    println("Text after undo: '${doc.text}'")
    println(doc.applyCommand(ClearCommand(doc)))
    println("Text: '${doc.text}'")
    println(doc.undoLast())
    println("Text after undo: '${doc.text}'")

    // Factory pattern
    printSection("Factory")
    val shapes = ArrayList<Shape>()
    val circle = createShape("circle", 5, 0, 0, 0)
    if (circle != null) shapes.add(circle)
    val rect = createShape("rectangle", 4, 6, 0, 0)
    if (rect != null) shapes.add(rect)
    val tri = createShape("triangle", 3, 4, 5, 4)
    if (tri != null) shapes.add(tri)
    val unknown = createShape("hexagon", 1, 0, 0, 0)
    val unknownStr = if (unknown == null) "null" else unknown.describe()
    println("Unknown shape: $unknownStr")
    for (shape in shapes) {
        println("${shape.describe()}: area=${shape.area()}, perimeter=${shape.perimeter()}")
    }

    // Decorator pattern
    printSection("Decorator")
    val plain = buildCoffee(false, false, false)
    println("${plain.description()} costs ${plain.cost()}")
    val withMilk = buildCoffee(true, false, false)
    println("${withMilk.description()} costs ${withMilk.cost()}")
    val fancy = buildCoffee(true, true, true)
    println("${fancy.description()} costs ${fancy.cost()}")

    // State pattern
    printSection("State")
    val controller = TrafficController()
    println("Initial: ${controller.currentState()} (${controller.currentAction()})")
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println("Log entries: ${controller.log.size}")
}

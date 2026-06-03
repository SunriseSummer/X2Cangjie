package proj_patterns

import std.collection.*
import std.deriving.*

@Derive[Equatable]

func printSection(title: String) {
    println("=== ${title} ===")
}

main() {
    printSection("Observer")
    let bus = EventBus()
    let logAll = LogObserver("AllLogger")
    let errorFilter = FilterObserver("ErrorFilter", "error")
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
        println("  ${log}")
    }
    printSection("Strategy")
    let calc = Calculator()
    println("Strategy: ${calc.currentStrategy()}")
    println("10 + 5 = ${calc.calculate(10, 5)}")
    calc.setStrategy(SubtractStrategy())
    println("Strategy: ${calc.currentStrategy()}")
    println("10 - 5 = ${calc.calculate(10, 5)}")
    calc.setStrategy(MultiplyStrategy())
    println("Strategy: ${calc.currentStrategy()}")
    println("10 * 5 = ${calc.calculate(10, 5)}")
    printSection("Command")
    let doc = TextDocument()
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
    printSection("Factory")
    let shapes = ArrayList<Shape>()
    let circle = createShape("circle", 5, 0, 0, 0)
    if (let Some(circle) <- circle) {
        shapes.add(circle)
    }
    let rect = createShape("rectangle", 4, 6, 0, 0)
    if (let Some(rect) <- rect) {
        shapes.add(rect)
    }
    let tri = createShape("triangle", 3, 4, 5, 4)
    if (let Some(tri) <- tri) {
        shapes.add(tri)
    }
    let unknown = createShape("hexagon", 1, 0, 0, 0)
    let unknownStr = if (let Some(unknown) <- unknown) {
        unknown.describe()
    } else {
        "null"
    }
    println("Unknown shape: ${unknownStr}")
    for (shape in shapes) {
        println("${shape.describe()}: area=${shape.area()}, perimeter=${shape.perimeter()}")
    }
    printSection("Decorator")
    let plain = buildCoffee(false, false, false)
    println("${plain.description()} costs ${plain.cost()}")
    let withMilk = buildCoffee(true, false, false)
    println("${withMilk.description()} costs ${withMilk.cost()}")
    let fancy = buildCoffee(true, true, true)
    println("${fancy.description()} costs ${fancy.cost()}")
    printSection("State")
    let controller = TrafficController()
    println("Initial: ${controller.currentState()} (${controller.currentAction()})")
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println(controller.advance())
    println("Log entries: ${controller.log.size}")
}

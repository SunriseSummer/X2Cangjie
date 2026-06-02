package proj_patterns

import std.collection.*
import std.deriving.*

interface Command {
    func execute(): String
    func undo(): String
    func describe(): String
}

class TextDocument {
    var text: String = ""
    let history = ArrayList<Command>()
    func applyCommand(cmd: Command): String {
        let result = cmd.execute()
        history.add(cmd)
        return result
    }
    func undoLast(): String {
        if (history.isEmpty()) {
            return "Nothing to undo"
        }
        let cmd = history.remove(at: history.size - 1)
        return cmd.undo()
    }
    func historyLog(): ArrayList<String> {
        let result = ArrayList<String>()
        for (cmd in history) {
            result.add(cmd.describe())
        }
        return result
    }
}

class AppendCommand <: Command {
    let doc: TextDocument
    let content: String
    init(doc: TextDocument, content: String) {
        this.doc = doc
        this.content = content
    }
    public override func execute(): String {
        doc.text = doc.text.toString() + content
        return "Appended: '${content}'"
    }
    public override func undo(): String {
        doc.text = doc.text[0..doc.text.size - content.size]
        return "Undone append: '${content}'"
    }
    public override func describe(): String {
        return "Append('${content}')"
    }
}

class ClearCommand <: Command {
    let doc: TextDocument
    init(doc: TextDocument) {
        this.doc = doc
    }
    var savedText: String = ""
    public override func execute(): String {
        savedText = doc.text
        doc.text = ""
        return "Cleared text (was: '${savedText}')"
    }
    public override func undo(): String {
        doc.text = savedText
        return "Restored text: '${savedText}'"
    }
    public override func describe(): String {
        return "Clear"
    }
}

interface Coffee {
    func cost(): Int64
    func description(): String
}

class SimpleCoffee <: Coffee {
    public override func cost(): Int64 {
        return 5
    }
    public override func description(): String {
        return "Simple coffee"
    }
}

class MilkDecorator <: Coffee {
    let inner: Coffee
    init(inner: Coffee) {
        this.inner = inner
    }
    public override func cost(): Int64 {
        return inner.cost() + 2
    }
    public override func description(): String {
        return inner.description().toString() + " + milk"
    }
}

class SugarDecorator <: Coffee {
    let inner: Coffee
    init(inner: Coffee) {
        this.inner = inner
    }
    public override func cost(): Int64 {
        return inner.cost() + 1
    }
    public override func description(): String {
        return inner.description().toString() + " + sugar"
    }
}

class WhipDecorator <: Coffee {
    let inner: Coffee
    init(inner: Coffee) {
        this.inner = inner
    }
    public override func cost(): Int64 {
        return inner.cost() + 3
    }
    public override func description(): String {
        return inner.description().toString() + " + whip"
    }
}

func buildCoffee(addMilk: Bool, addSugar: Bool, addWhip: Bool): Coffee {
    var coffee: Coffee = SimpleCoffee()
    if (addMilk) {
        coffee = MilkDecorator(coffee)
    }
    if (addSugar) {
        coffee = SugarDecorator(coffee)
    }
    if (addWhip) {
        coffee = WhipDecorator(coffee)
    }
    return coffee
}

interface Shape {
    func area(): Int64
    func perimeter(): Int64
    func describe(): String
}

class Circle <: Shape {
    let radius: Int64
    init(radius: Int64) {
        this.radius = radius
    }
    public override func area(): Int64 {
        return ((314 * radius) * radius) / 100
    }
    public override func perimeter(): Int64 {
        return (628 * radius) / 100
    }
    public override func describe(): String {
        return "Circle(radius=${radius})"
    }
}

class Rectangle <: Shape {
    let width: Int64
    let height: Int64
    init(width: Int64, height: Int64) {
        this.width = width
        this.height = height
    }
    public override func area(): Int64 {
        return width * height
    }
    public override func perimeter(): Int64 {
        return 2 * (width + height)
    }
    public override func describe(): String {
        return "Rectangle(width=${width}, height=${height})"
    }
}

class Triangle <: Shape {
    let base: Int64
    let triangleHeight: Int64
    let side1: Int64
    let side2: Int64
    init(base: Int64, triangleHeight: Int64, side1: Int64, side2: Int64) {
        this.base = base
        this.triangleHeight = triangleHeight
        this.side1 = side1
        this.side2 = side2
    }
    public override func area(): Int64 {
        return (base * triangleHeight) / 2
    }
    public override func perimeter(): Int64 {
        return (base + side1) + side2
    }
    public override func describe(): String {
        return "Triangle(base=${base}, height=${triangleHeight})"
    }
}

func createShape(shapeType: String, param1: Int64, param2: Int64, param3: Int64, param4: Int64): ?Shape {
    return match (shapeType) {
        case "circle" => Circle(param1)
        case "rectangle" => Rectangle(param1, param2)
        case "triangle" => Triangle(param1, param2, param3, param4)
        case _ => None}
}

interface Observer {
    func onEvent(event: String): Unit
    func observerName(): String
}

class EventBus {
    let listeners = ArrayList<Observer>()
    func subscribe(observer: Observer) {
        listeners.add(observer)
    }
    func publish(event: String) {
        for (listener in listeners) {
            listener.onEvent(event)
        }
    }
    func subscriberCount(): Int64 {
        return listeners.size
    }
}

class LogObserver <: Observer & ToString {
    let name: String
    init(name: String) {
        this.name = name
    }
    let logs = ArrayList<String>()
    public override func onEvent(event: String) {
        logs.add("[${name}] received: ${event}")
    }
    public override func observerName(): String {
        return name
    }
    public override func toString(): String {
        let builder = StringBuilder()
        for (log in logs) {
            builder.append(log)
            builder.append("\n")
        }
        return builder.toString().trimAscii()
    }
}

class FilterObserver <: Observer {
    let name: String
    let keyword: String
    init(name: String, keyword: String) {
        this.name = name
        this.keyword = keyword
    }
    let logs = ArrayList<String>()
    public override func onEvent(event: String) {
        if (event.contains(keyword)) {
            logs.add("[${name}] matched '${keyword}' in: ${event}")
        }
    }
    public override func observerName(): String {
        return name
    }
}

@Derive[Equatable]
enum TrafficLight <: ToString {
    | RED | YELLOW | GREEN
    public func toString(): String {
    return match (this) {
                case RED => "RED"
            case YELLOW => "YELLOW"
            case GREEN => "GREEN"
}
    }
}

func nextLight(light: TrafficLight): TrafficLight {
    return match (light) {
        case TrafficLight.RED => TrafficLight.GREEN
        case TrafficLight.GREEN => TrafficLight.YELLOW
        case TrafficLight.YELLOW => TrafficLight.RED}
}

func lightAction(light: TrafficLight): String {
    return match (light) {
        case TrafficLight.RED => "Stop"
        case TrafficLight.YELLOW => "Caution"
        case TrafficLight.GREEN => "Go"}
}

class TrafficController {
    var state: TrafficLight = TrafficLight.RED
    let log = ArrayList<String>()
    func currentState(): String {
        return state.toString()
    }
    func currentAction(): String {
        return lightAction(state)
    }
    func advance(): String {
        let oldState = state
        state = nextLight(state)
        let msg = "${oldState} -> ${state} (${lightAction(state)})"
        log.add(msg)
        return msg
    }
}

interface Strategy {
    func execute(a: Int64, b: Int64): Int64
    func name(): String
}

class AddStrategy <: Strategy {
    public override func execute(a: Int64, b: Int64): Int64 {
        return a + b
    }
    public override func name(): String {
        return "Add"
    }
}

class SubtractStrategy <: Strategy {
    public override func execute(a: Int64, b: Int64): Int64 {
        return a - b
    }
    public override func name(): String {
        return "Subtract"
    }
}

class MultiplyStrategy <: Strategy {
    public override func execute(a: Int64, b: Int64): Int64 {
        return a * b
    }
    public override func name(): String {
        return "Multiply"
    }
}

class Calculator {
    var strategy: Strategy = AddStrategy()
    func setStrategy(s: Strategy) {
        strategy = s
    }
    func calculate(a: Int64, b: Int64): Int64 {
        return strategy.execute(a, b)
    }
    func currentStrategy(): String {
        return strategy.name()
    }
}

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
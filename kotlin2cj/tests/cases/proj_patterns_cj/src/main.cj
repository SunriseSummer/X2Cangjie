package proj_patterns

import std.collection.*
import std.deriving.*
import std.sort.*

class LogLevel <: ToString & Equatable<LogLevel> {
    let _ordinal: Int64
    public let weight: Int64
    init(_ordinal: Int64, weight: Int64) {
        this._ordinal = _ordinal
        this.weight = weight
    }
    public static let DEBUG = LogLevel(0, 1)
    public static let INFO = LogLevel(1, 2)
    public static let WARN = LogLevel(2, 3)
    public static let ERROR = LogLevel(3, 4)
    public func toString(): String {
            if (this == LogLevel.DEBUG) { return "DEBUG" }
            if (this == LogLevel.INFO) { return "INFO" }
            if (this == LogLevel.WARN) { return "WARN" }
            if (this == LogLevel.ERROR) { return "ERROR" }
return "LogLevel(?)"
    }
    public operator func ==(rhs: LogLevel): Bool {
        return this._ordinal == rhs._ordinal
    }
    public operator func !=(rhs: LogLevel): Bool {
        return !(this == rhs)
    }
}

class LogMessage <: ToString {
    let level: LogLevel
    let channel: String
    let text: String
    init(level: LogLevel, channel: String, text: String) {
        this.level = level
        this.channel = channel
        this.text = text
    }
    public func toString(): String {
        return "LogMessage(level=${this.level}, channel=${this.channel}, text=${this.text})"
    }
}

abstract class Logger {
    let loggerName: String
    let threshold: LogLevel
    init(loggerName: String, threshold: LogLevel) {
        this.loggerName = loggerName
        this.threshold = threshold
    }
    var next: ?Logger = None
    let handled = ArrayList<String>()
    public open func setNext(logger: Logger): Logger {
        next = logger
        return logger
    }
    public open func log(message: LogMessage): ArrayList<String> {
        let lines = ArrayList<String>()
        if (message.level.weight >= threshold.weight) {
            let rendered = write(message)
            handled.add(rendered)
            lines.add("${loggerName} handled ${message.level}:${message.channel}:${message.text}")
        } else {
            lines.add("${loggerName} skipped ${message.level}:${message.channel}:${message.text}")
        }
        if (let Some(next) <- next) {
            for (line in next.getOrThrow().log(message)) {
                lines.add(line)
            }
        }
        return lines
    }
    public func write(message: LogMessage): String
    public open func summary(): String {
        let entriesText = String.join(collectArray<String>(handled.iterator().map({e => e.toString()})), delimiter: " || ")
        return "${loggerName} stored=${handled.size} entries=${entriesText}"
    }
}

class ConsoleLogger <: Logger {
    init(name: String, threshold: LogLevel) {
        super(name, threshold)
    }
    public override func write(message: LogMessage): String {
        return "console:${message.level}:${message.channel}:${message.text}"
    }
}

class FileLogger <: Logger {
    init(name: String, threshold: LogLevel) {
        super(name, threshold)
    }
    public override func write(message: LogMessage): String {
        return "file:${message.level}:${message.channel}:${message.text}"
    }
}

class ErrorLogger <: Logger {
    init(name: String, threshold: LogLevel) {
        super(name, threshold)
    }
    public override func write(message: LogMessage): String {
        return "error:${message.level}:${message.channel}:${message.text.manualUpper()}"
    }
}

interface Command {
    func execute(): String
    func undo(): String
    func describe(): String
}

class TextEditor {
    init(initialText!: String = "") {
    }
    var text: String = initialText
    let undoStack = ArrayList<Command>()
    let redoStack = ArrayList<Command>()
    let timeline = ArrayList<String>()
    func normalizePosition(position: Int64): Int64 {
        if (position < 0) {
            return 0
        }
        if (position > text.size) {
            return text.size
        }
        return position
    }
    func insertRaw(position: Int64, content: String) {
        let safe = normalizePosition(position)
        let prefix = text[0..safe]
        let suffix = text[safe..text.size]
        text = (prefix + content) + suffix
    }
    func deleteRaw(position: Int64, length: Int64): String {
        if (length <= 0) {
            return ""
        }
        let safe = normalizePosition(position)
        var end = safe + length
        if (end > text.size) {
            end = text.size
        }
        let removed = text[safe..end]
        text = text[0..safe] + text[end..text.size]
        return removed
    }
    func findFirst(target: String): Int64 {
        if (target.size == 0) {
            return 0
        }
        var start = 0
        while (start <= (text.size - target.size)) {
            let piece = text[start..start + target.size]
            if (piece == target) {
                return start
            }
            start += 1
        }
        return -1
    }
    func replaceFirstRaw(target: String, replacement: String): Bool {
        if (!text.contains(target)) {
            return false
        }
        let index = findFirst(target)
        if (index < 0) {
            return false
        }
        text = (text[0..index] + replacement) + text[index + target.size..text.size]
        return true
    }
    func replaceAllRaw(target: String, replacement: String): Int64 {
        var count = 0
        while (text.contains(target)) {
            let changed = replaceFirstRaw(target, replacement)
            if (!changed) {
                break
            }
            count += 1
        }
        return count
    }
    func executeCommand(command: Command): String {
        let result = command.execute()
        undoStack.add(command)
        redoStack.clear()
        timeline.add("execute:${command.describe()} => ${text}")
        return result
    }
    func undo(): String {
        if (undoStack.size == 0) {
            let message = "undo: nothing"
            timeline.add(message)
            return message
        }
        let command = undoStack.remove(at: undoStack.size - 1)
        let result = command.undo()
        redoStack.add(command)
        timeline.add("undo:${command.describe()} => ${text}")
        return result
    }
    func redo(): String {
        if (redoStack.size == 0) {
            let message = "redo: nothing"
            timeline.add(message)
            return message
        }
        let command = redoStack.remove(at: redoStack.size - 1)
        let result = command.execute()
        undoStack.add(command)
        timeline.add("redo:${command.describe()} => ${text}")
        return result
    }
    func snapshot(): String {
        return if (text == "") {
            "<empty>"
        } else {
            text
        }
    }
    func historySize(): Int64 {
        return undoStack.size
    }
    func redoSize(): Int64 {
        return redoStack.size
    }
}

class InsertCommand <: Command {
    let editor: TextEditor
    let position: Int64
    let content: String
    init(editor: TextEditor, position: Int64, content: String) {
        this.editor = editor
        this.position = position
        this.content = content
    }
    var lastPosition = 0
    var executed = false
    public override func execute(): String {
        lastPosition = editor.normalizePosition(position)
        editor.insertRaw(lastPosition, content)
        executed = true
        return "insert '${content}' at ${lastPosition}"
    }
    public override func undo(): String {
        if (!executed) {
            return "undo insert skipped"
        }
        editor.deleteRaw(lastPosition, content.size)
        return "undo insert '${content}' at ${lastPosition}"
    }
    public override func describe(): String {
        return "Insert(position=${position}, content=${content})"
    }
}

class DeleteCommand <: Command {
    let editor: TextEditor
    let position: Int64
    let length: Int64
    init(editor: TextEditor, position: Int64, length: Int64) {
        this.editor = editor
        this.position = position
        this.length = length
    }
    var removedText = ""
    var actualPosition = 0
    var executed = false
    public override func execute(): String {
        actualPosition = editor.normalizePosition(position)
        removedText = editor.deleteRaw(actualPosition, length)
        executed = true
        return "delete '${removedText}' at ${actualPosition}"
    }
    public override func undo(): String {
        if (!executed) {
            return "undo delete skipped"
        }
        editor.insertRaw(actualPosition, removedText)
        return "undo delete '${removedText}' at ${actualPosition}"
    }
    public override func describe(): String {
        return "Delete(position=${position}, length=${length})"
    }
}

class ReplaceCommand <: Command {
    let editor: TextEditor
    let target: String
    let replacement: String
    let replaceAll: Bool
    init(editor: TextEditor, target: String, replacement: String, replaceAll!: Bool = false) {
        this.editor = editor
        this.target = target
        this.replacement = replacement
        this.replaceAll = replaceAll
    }
    var beforeText = ""
    var changedCount = 0
    public override func execute(): String {
        beforeText = editor.text
        changedCount = if (replaceAll) {
            editor.replaceAllRaw(target, replacement)
        } else {
            if (editor.replaceFirstRaw(target, replacement)) {
                1
            } else {
                0
            }
        }
        return "replace '${target}' with '${replacement}' count=${changedCount}"
    }
    public override func undo(): String {
        let current = editor.text
        editor.text = beforeText
        return "undo replace restore '${current}'"
    }
    public override func describe(): String {
        return "Replace(target=${target}, replacement=${replacement}, replaceAll=${replaceAll})"
    }
}

interface FileSystemNode {
    func size(): Int64
    func list(indent!: String = ""): ArrayList<String>
    func find(name: String): ?FileSystemNode
    func countNodes(): Int64
    func kind(): String
}

class FileNode <: FileSystemNode {
    let nodeName: String
    let content: String
    init(nodeName: String, content: String) {
        this.nodeName = nodeName
        this.content = content
    }
    public override func size(): Int64 {
        return content.size
    }
    public override func list(indent: String): ArrayList<String> {
        return ArrayList(["${indent}- FILE ${nodeName} (${size()})"])
    }
    public override func find(name: String): ?FileSystemNode {
        return if (nodeName == name) {
            this
        } else {
            None
        }
    }
    public override func countNodes(): Int64 {
        return 1
    }
    public override func kind(): String {
        return "file"
    }
    func preview(): String {
        return if (content.size <= 12) {
            content
        } else {
            content[0..12]
        }
    }
}

class DirectoryNode <: FileSystemNode {
    let nodeName: String
    init(nodeName: String) {
        this.nodeName = nodeName
    }
    let children = ArrayList<FileSystemNode>()
    func add(node: FileSystemNode): DirectoryNode {
        children.add(node)
        return this
    }
    func remove(name: String): Bool {
        var i = 0
        while (i < children.size) {
            if (children[i].nodeName == name) {
                children.remove(at: i)
                return true
            }
            i += 1
        }
        return false
    }
    func childNames(): ArrayList<String> {
        let result = ArrayList<String>()
        for (child in children) {
            result.add(child.nodeName)
        }
        return result
    }
    public override func size(): Int64 {
        var sum = 0
        for (child in children) {
            sum += child.size()
        }
        return sum
    }
    public override func list(indent: String): ArrayList<String> {
        let lines = ArrayList<String>()
        lines.add("${indent}+ DIR ${nodeName} (${size()})")
        for (child in children) {
            for (line in child.list(indent + "  ")) {
                lines.add(line)
            }
        }
        return lines
    }
    public override func find(name: String): ?FileSystemNode {
        if (nodeName == name) {
            return this
        }
        for (child in children) {
            let found = child.find(name)
            if (let Some(found) <- found) {
                return found
            }
        }
        return None
    }
    public override func countNodes(): Int64 {
        var total = 1
        for (child in children) {
            total += child.countNodes()
        }
        return total
    }
    public override func kind(): String {
        return "directory"
    }
    func flatten(prefix!: String = ""): ArrayList<String> {
        let lines = ArrayList<String>()
        let current = if (prefix == "") {
            nodeName
        } else {
            "${prefix}/${nodeName}"
        }
        lines.add(current)
        for (child in children) {
            if ((child is DirectoryNode)) {
                for (line in child.flatten(current)) {
                    lines.add(line)
                }
            } else {
                lines.add("${current}/${child.nodeName}")
            }
        }
        return lines
    }
}

interface Coffee {
    func cost(): Int64
    func description(): String
    func ingredients(): ArrayList<String>
}

class SimpleCoffee <: Coffee {
    let bean: String
    init(bean!: String = "House Blend") {
        this.bean = bean
    }
    public override func cost(): Int64 {
        return 5
    }
    public override func description(): String {
        return "${bean} coffee"
    }
    public override func ingredients(): ArrayList<String> {
        return ArrayList([bean, "water"])
    }
}

abstract class CoffeeDecorator <: Coffee {
    let inner: Coffee
    init(inner: Coffee) {
        this.inner = inner
    }
    public open override func ingredients(): ArrayList<String> {
        let items = ArrayList<String>()
        for (item in inner.ingredients()) {
            items.add(item)
        }
        return items
    }
}

class MilkDecorator <: CoffeeDecorator {
    let shots: Int64
    init(inner: Coffee, shots!: Int64 = 1) {
        super(inner)
        this.shots = shots
    }
    public override func cost(): Int64 {
        return inner.cost() + (shots * 2)
    }
    public override func description(): String {
        return inner.description().toString() + " + milk x${shots}"
    }
    public override func ingredients(): ArrayList<String> {
        let items = `super`.ingredients()
        var i = 0
        while (i < shots) {
            items.add("milk")
            i += 1
        }
        return items
    }
}

class SugarDecorator <: CoffeeDecorator {
    let cubes: Int64
    init(inner: Coffee, cubes!: Int64 = 1) {
        super(inner)
        this.cubes = cubes
    }
    public override func cost(): Int64 {
        return inner.cost() + cubes
    }
    public override func description(): String {
        return inner.description().toString() + " + sugar x${cubes}"
    }
    public override func ingredients(): ArrayList<String> {
        let items = `super`.ingredients()
        var i = 0
        while (i < cubes) {
            items.add("sugar")
            i += 1
        }
        return items
    }
}

class WhipDecorator <: CoffeeDecorator {
    let layers: Int64
    init(inner: Coffee, layers!: Int64 = 1) {
        super(inner)
        this.layers = layers
    }
    public override func cost(): Int64 {
        return inner.cost() + (layers * 3)
    }
    public override func description(): String {
        return inner.description().toString() + " + whip x${layers}"
    }
    public override func ingredients(): ArrayList<String> {
        let items = `super`.ingredients()
        var i = 0
        while (i < layers) {
            items.add("whip")
            i += 1
        }
        return items
    }
}

class CoffeeBuilder {
    init(baseBean!: String = "House Blend") {
    }
    var current: Coffee = SimpleCoffee(bean: baseBean)
    func addMilk(shots!: Int64 = 1): CoffeeBuilder {
        current = MilkDecorator(current, shots: shots)
        return this
    }
    func addSugar(cubes!: Int64 = 1): CoffeeBuilder {
        current = SugarDecorator(current, cubes: cubes)
        return this
    }
    func addWhip(layers!: Int64 = 1): CoffeeBuilder {
        current = WhipDecorator(current, layers: layers)
        return this
    }
    func build(): Coffee {
        return current
    }
}

func coffeeReceiptLines(coffee: Coffee): ArrayList<String> {
    let lines = ArrayList<String>()
    lines.add("drink=${coffee.description()}")
    lines.add("cost=${coffee.cost()}")
    let ingredientText = String.join(collectArray<String>(coffee.ingredients().iterator().map({e => e.toString()})), delimiter: ", ")
    lines.add("ingredients=${ingredientText}")
    return lines
}

interface Shape {
    func name(): String
    func area(): Int64
    func perimeter(): Int64
    func describe(): String
    func scale(factor: Int64): Shape
}

class ShapeSpec <: ToString {
    let `type`: String
    let first: Int64
    let second: Int64
    let third: Int64
    init(`type`: String, first: Int64, second!: Int64 = 0, third!: Int64 = 0) {
        this.`type` = `type`
        this.first = first
        this.second = second
        this.third = third
    }
    public func toString(): String {
        return "ShapeSpec(`type`=${this.`type`}, first=${this.first}, second=${this.second}, third=${this.third})"
    }
}

class Circle <: Shape {
    let radius: Int64
    init(radius: Int64) {
        this.radius = radius
    }
    public override func name(): String {
        return "Circle"
    }
    public override func area(): Int64 {
        return (radius * radius) * 3
    }
    public override func perimeter(): Int64 {
        return radius * 6
    }
    public override func describe(): String {
        return "Circle(radius=${radius}, area=${area()}, perimeter=${perimeter()})"
    }
    public override func scale(factor: Int64): Shape {
        return Circle(radius * factor)
    }
}

class Rectangle <: Shape {
    let width: Int64
    let height: Int64
    init(width: Int64, height: Int64) {
        this.width = width
        this.height = height
    }
    public override func name(): String {
        return "Rectangle"
    }
    public override func area(): Int64 {
        return width * height
    }
    public override func perimeter(): Int64 {
        return (width + height) * 2
    }
    public override func describe(): String {
        return "Rectangle(width=${width}, height=${height}, area=${area()}, perimeter=${perimeter()})"
    }
    public override func scale(factor: Int64): Shape {
        return Rectangle(width * factor, height * factor)
    }
}

class Triangle <: Shape {
    let base: Int64
    let height: Int64
    let side: Int64
    init(base: Int64, height: Int64, side: Int64) {
        this.base = base
        this.height = height
        this.side = side
    }
    public override func name(): String {
        return "Triangle"
    }
    public override func area(): Int64 {
        return (base * height) / 2
    }
    public override func perimeter(): Int64 {
        return (base + side) + side
    }
    public override func describe(): String {
        return "Triangle(base=${base}, height=${height}, side=${side}, area=${area()}, perimeter=${perimeter()})"
    }
    public override func scale(factor: Int64): Shape {
        return Triangle(base * factor, height * factor, side * factor)
    }
}

open class ShapeFactory {
    public open func createShape(`type`: String, first: Int64, second!: Int64 = 0, third!: Int64 = 0): ?Shape {
        return match (`type`.manualLower()) {
            case "circle" => Circle(first)
            case "rectangle" => Rectangle(first, second)
            case "triangle" => Triangle(first, second, third)
            case _ => None}
    }
    public open func createBatch(specs: ArrayList<ShapeSpec>): ArrayList<Shape> {
        let shapes = ArrayList<Shape>()
        for (spec in specs) {
            let shape = createShape(spec.`type`, spec[0], second: spec[1], third: spec[2])
            if (let Some(shape) <- shape) {
                shapes.add(shape)
            }
        }
        return shapes
    }
    public open func totalArea(shapes: ArrayList<Shape>): Int64 {
        var sum = 0
        for (shape in shapes) {
            sum += shape.area()
        }
        return sum
    }
    public open func totalPerimeter(shapes: ArrayList<Shape>): Int64 {
        var sum = 0
        for (shape in shapes) {
            sum += shape.perimeter()
        }
        return sum
    }
    public open static func standardSpecs(): ArrayList<ShapeSpec> {
        return ArrayList([ShapeSpec("circle", 3), ShapeSpec("rectangle", 4, second: 5), ShapeSpec("triangle", 6, second: 4, third: 5)])
    }
}

class ColoredShape <: ToString {
    let color: String
    let shape: Shape
    init(color: String, shape: Shape) {
        this.color = color
        this.shape = shape
    }
    func describe(): String {
        return "${color} ${shape.describe()}"
    }
    func tag(): String {
        return "${color.manualUpper()}-${shape.name().manualUpper()}"
    }
    public func toString(): String {
        return "ColoredShape(color=${this.color}, shape=${this.shape})"
    }
}

interface AbstractShapeFactory {
    func paletteName(): String
    func createPrimaryShape(): ColoredShape
    func createAccentShape(): ColoredShape
    func createNeutralShape(): ColoredShape
}

class ColoredShapeFactory <: ShapeFactory & AbstractShapeFactory {
    let color: String
    init(color: String) {
        this.color = color
    }
    public override func paletteName(): String {
        return "${color}-theme"
    }
    func createColoredShape(`type`: String, first: Int64, second!: Int64 = 0, third!: Int64 = 0): ?ColoredShape {
        let shape = createShape(`type`, first, second: second, third: third)
        return if (let Some(shape) <- shape) {
            ColoredShape(color, shape)
        } else {
            None
        }
    }
    public override func createPrimaryShape(): ColoredShape {
        return match (color.manualLower()) {
            case "red" => ColoredShape(color, Circle(4))
            case "blue" => ColoredShape(color, Rectangle(5, 2))
            case _ => ColoredShape(color, Triangle(6, 4, 5))}
    }
    public override func createAccentShape(): ColoredShape {
        return match (color.manualLower()) {
            case "red" => ColoredShape(color, Rectangle(3, 6))
            case "blue" => ColoredShape(color, Triangle(5, 4, 4))
            case _ => ColoredShape(color, Circle(2))}
    }
    public override func createNeutralShape(): ColoredShape {
        return ColoredShape("gray", Rectangle(2, 2))
    }
    func buildShowcase(): ArrayList<ColoredShape> {
        let list = ArrayList<ColoredShape>()
        list.add(createPrimaryShape())
        list.add(createAccentShape())
        list.add(createNeutralShape())
        return list
    }
    func summary(shapes: ArrayList<ColoredShape>): String {
        let parts = ArrayList<String>()
        for (shape in shapes) {
            parts.add(shape.tag())
        }
        return String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: ", ")
    }
}

class Event <: ToString {
    let `type`: String
    let source: String
    let payload: String
    let priority: Int64
    init(`type`: String, source: String, payload: String, priority!: Int64 = 0) {
        this.`type` = `type`
        this.source = source
        this.payload = payload
        this.priority = priority
    }
    public func toString(): String {
        return "Event(`type`=${this.`type`}, source=${this.source}, payload=${this.payload}, priority=${this.priority})"
    }
}

interface EventListener {
    func onEvent(event: Event): String
}

abstract class BaseEventListener <: EventListener {
    let listenerName: String
    init(listenerName: String) {
        this.listenerName = listenerName
    }
    let history = ArrayList<String>()
    var handledCount = 0
    public open func remember(message: String): String {
        handledCount += 1
        history.add(message)
        return message
    }
    public open func lastMessage(): String {
        return if (history.size == 0) {
            "<none>"
        } else {
            history[history.size - 1]
        }
    }
    public open func describeHistory(): String {
        return String.join(collectArray<String>(history.iterator().map({e => e.toString()})), delimiter: " || ")
    }
}

class LoggingListener <: BaseEventListener {
    let channel: String
    init(name: String, channel: String) {
        super(name)
        this.channel = channel
    }
    public override func onEvent(event: Event): String {
        let message = "[${channel}] ${listenerName} logged ${event.`type`} from ${event.source} payload=${event.payload} priority=${event.priority}"
        return remember(message)
    }
}

class CountingListener <: BaseEventListener {
    init(name: String) {
        super(name)
    }
    let typeCounts = HashMap<String, Int64>()
    let sourceCounts = HashMap<String, Int64>()
    public override func onEvent(event: Event): String {
        let currentType = typeCounts.get(event.`type`) ?? 0
        typeCounts[event.`type`] = currentType + 1
        let currentSource = sourceCounts.get(event.source) ?? 0
        sourceCounts[event.source] = currentSource + 1
        let message = "${listenerName} counted ${event.`type`} for ${event.source} -> type=${typeCounts[event.`type`]} source=${sourceCounts[event.source]}"
        return remember(message)
    }
    func typeSummary(): String {
        let keys = ArrayList<String>()
        for (key in typeCounts.keys()) {
            keys.add(key)
        }
        let ordered = ({ => let _s = collectArrayList(keys.iterator()); sort(_s, stable: true); _s })()
        let parts = ArrayList<String>()
        for (key in ordered) {
            parts.add("${key}=${typeCounts.get(key) ?? 0}")
        }
        return String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: ", ")
    }
    func sourceSummary(): String {
        let keys = ArrayList<String>()
        for (key in sourceCounts.keys()) {
            keys.add(key)
        }
        let ordered = ({ => let _s = collectArrayList(keys.iterator()); sort(_s, stable: true); _s })()
        let parts = ArrayList<String>()
        for (key in ordered) {
            parts.add("${key}=${sourceCounts.get(key) ?? 0}")
        }
        return String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: ", ")
    }
}

class FilteringListener <: BaseEventListener {
    let allowedType: String
    let sink: ArrayList<String>
    init(name: String, allowedType: String, sink: ArrayList<String>) {
        super(name)
        this.allowedType = allowedType
        this.sink = sink
    }
    public override func onEvent(event: Event): String {
        let accepted = event.`type` == allowedType
        let message = if (accepted) {
            "${listenerName} accepted ${event.`type`} from ${event.source}"
        } else {
            "${listenerName} ignored ${event.`type`} from ${event.source}"
        }
        if (accepted) {
            sink.add("accepted:${event.source}:${event.payload}")
        }
        return remember(message)
    }
}

class AuditListener <: BaseEventListener {
    init(name: String) {
        super(name)
    }
    public override func onEvent(event: Event): String {
        let normalized = event.payload.trimAscii().manualUpper().replace(" ", "_")
        let message = "${listenerName} audit ${event.`type`}:${event.source}:${normalized}"
        return remember(message)
    }
}

class EventBus {
    let busName: String
    init(busName: String) {
        this.busName = busName
    }
    let topics = ArrayList<String>()
    let listeners = ArrayList<ArrayList<EventListener>>()
    let publishLog = ArrayList<String>()
    func topicIndex(topic: String): Int64 {
        var i = 0
        while (i < topics.size) {
            if (topics[i] == topic) {
                return i
            }
            i += 1
        }
        return -1
    }
    func subscribe(topic: String, listener: EventListener) {
        let index = topicIndex(topic)
        if (index >= 0) {
            listeners[index].add(listener)
        } else {
            topics.add(topic)
            let bucket = ArrayList<EventListener>()
            bucket.add(listener)
            listeners.add(bucket)
        }
    }
    func unsubscribe(topic: String, listenerName: String): Bool {
        let index = topicIndex(topic)
        if (index < 0) {
            return false
        }
        let bucket = listeners[index]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i].listenerName == listenerName) {
                bucket.remove(at: i)
                return true
            }
            i += 1
        }
        return false
    }
    func publish(event: Event): ArrayList<String> {
        let messages = ArrayList<String>()
        publishLog.add("${event.`type`}@${event.source}:${event.payload}:${event.priority}")
        let index = topicIndex(event.`type`)
        if (index < 0) {
            messages.add("EventBus[${busName}] no listeners for ${event.`type`}")
            return messages
        }
        let bucket = listeners[index]
        if (bucket.size == 0) {
            messages.add("EventBus[${busName}] no listeners for ${event.`type`}")
            return messages
        }
        for (listener in bucket) {
            messages.add(listener.onEvent(event))
        }
        return messages
    }
    func listenerCount(topic: String): Int64 {
        let index = topicIndex(topic)
        return if (index < 0) {
            0
        } else {
            listeners[index].size
        }
    }
    func topicNames(): ArrayList<String> {
        let copy = ArrayList<String>()
        for (topic in topics) {
            copy.add(topic)
        }
        return copy
    }
    func describeSubscriptions(): ArrayList<String> {
        let lines = ArrayList<String>()
        var i = 0
        while (i < topics.size) {
            let names = ArrayList<String>()
            for (listener in listeners[i]) {
                names.add(listener.listenerName)
            }
            let joinedNames = String.join(collectArray<String>(names.iterator().map({e => e.toString()})), delimiter: ", ")
            lines.add("${topics[i]} -> ${joinedNames}")
            i += 1
        }
        return lines
    }
    func publishSummary(): String {
        return String.join(collectArray<String>(publishLog.iterator().map({e => e.toString()})), delimiter: " | ")
    }
}

class Product <: ToString & Equatable<Product> {
    let _ordinal: Int64
    public let label: String
    public let price: Int64
    init(_ordinal: Int64, label: String, price: Int64) {
        this._ordinal = _ordinal
        this.label = label
        this.price = price
    }
    public static let WATER = Product(0, "Water", 3)
    public static let JUICE = Product(1, "Juice", 5)
    public static let TEA = Product(2, "Tea", 4)
    public func toString(): String {
            if (this == Product.WATER) { return "WATER" }
            if (this == Product.JUICE) { return "JUICE" }
            if (this == Product.TEA) { return "TEA" }
return "Product(?)"
    }
    public operator func ==(rhs: Product): Bool {
        return this._ordinal == rhs._ordinal
    }
    public operator func !=(rhs: Product): Bool {
        return !(this == rhs)
    }
}

func allProducts(): ArrayList<Product> {
    return ArrayList([Product.WATER, Product.JUICE, Product.TEA])
}

open class MachineState {}

class IdleState <: MachineState {}

class HasMoneyState <: MachineState {
    let balance: Int64
    init(balance: Int64) {
        this.balance = balance
    }
}

class DispensingState <: MachineState {
    let product: Product
    let change: Int64
    init(product: Product, change: Int64) {
        this.product = product
        this.change = change
    }
}

class VendingMachine {
    init() {
        inventory[Product.WATER.label] = 2
        inventory[Product.JUICE.label] = 1
        inventory[Product.TEA.label] = 3
    }
    var state: MachineState = IdleState()
    let inventory = HashMap<String, Int64>()
    let log = ArrayList<String>()
    func stockOf(product: Product): Int64 {
        return inventory.get(product.label) ?? 0
    }
    func status(): String {
        let balanceText = match (state) {
            case state: IdleState => "Idle(balance=0)"
            case state: HasMoneyState => 
                let current = (state as HasMoneyState)
                "HasMoney(balance=${current.balance})"
            case state: DispensingState => 
                let current = (state as DispensingState)
                "Dispensing(product=${current.product.label}, change=${current.change})"
            case _ => throw Exception("")}
        let stockLines = ArrayList<String>()
        for (product in allProducts()) {
            stockLines.add("${product.label}=${stockOf(product)}")
        }
        let joinedStock = String.join(collectArray<String>(stockLines.iterator().map({e => e.toString()})), delimiter: ", ")
        return "${balanceText} stock[${joinedStock}]"
    }
    func insertCoin(amount: Int64): String {
        if (amount <= 0) {
            let message = "insert rejected amount=${amount}"
            log.add(message)
            return message
        }
        let message = match (state) {
            case state: IdleState => 
                state = HasMoneyState(amount)
                "inserted ${amount} -> balance ${amount}"
            case state: HasMoneyState => 
                let current = (state as HasMoneyState)
                let next = current.balance + amount
                state = HasMoneyState(next)
                "inserted ${amount} -> balance ${next}"
            case state: DispensingState => "insert blocked during dispensing"
            case _ => throw Exception("")}
        log.add(message)
        return message
    }
    func select(product: Product): String {
        let stock = stockOf(product)
        let message = match (state) {
            case state: IdleState => "select ${product.label} failed: no money"
            case state: HasMoneyState => 
                let current = (state as HasMoneyState)
                if (stock <= 0) {
                    "select ${product.label} failed: out of stock"
                } else if (current.balance < product.price) {
                    "select ${product.label} failed: need ${product.price - current.balance} more"
                } else {
                    let change = current.balance - product.price
                    inventory[product.label] = stock - 1
                    state = DispensingState(product, change)
                    "select ${product.label} accepted: change ${change}"
                }
            case state: DispensingState => "select ${product.label} blocked: dispensing"
            case _ => throw Exception("")}
        log.add(message)
        return message
    }
    func finishDispense(): String {
        let message = match (state) {
            case state: DispensingState => 
                let current = (state as DispensingState)
                state = IdleState()
                "dispensed ${current.product.label} change ${current.change}"
            case _ => "dispense skipped"}
        log.add(message)
        return message
    }
    func refund(): String {
        let message = match (state) {
            case state: HasMoneyState => 
                let current = (state as HasMoneyState)
                state = IdleState()
                "refund ${current.balance}"
            case state: IdleState => "refund 0"
            case state: DispensingState => "refund blocked during dispensing"
            case _ => throw Exception("")}
        log.add(message)
        return message
    }
    func auditLines(): ArrayList<String> {
        let lines = ArrayList<String>()
        var index = 1
        for (entry in log) {
            lines.add("${index}.${entry}")
            index += 1
        }
        return lines
    }
}

extend MutableList<Int64> {
    func swapAt(first: Int64, second: Int64) {
        let temp = this[first]
        this[first] = this[second]
        this[second] = temp
    }
}

extend MutableList<Int64> {
    func asNumberString(): String {
        return String.join(collectArray<String>(this.iterator().map({e => e.toString()})), delimiter: ", ")
    }
}

interface SortStrategy {
    func sort(values: ArrayList<Int64>): ArrayList<Int64>
    func describe(): String
}

class SortReport <: ToString {
    let strategyName: String
    let before: String
    let after: String
    let passes: Int64
    let swaps: Int64
    init(strategyName: String, before: String, after: String, passes: Int64, swaps: Int64) {
        this.strategyName = strategyName
        this.before = before
        this.after = after
        this.passes = passes
        this.swaps = swaps
    }
    public func toString(): String {
        return "SortReport(strategyName=${this.strategyName}, before=${this.before}, after=${this.after}, passes=${this.passes}, swaps=${this.swaps})"
    }
}

class BubbleSortStrategy <: SortStrategy {
    let ascending: Bool
    let label: String
    init(ascending!: Bool = true, label!: String = "bubble") {
        this.ascending = ascending
        this.label = label
    }
    let strategyName: String = if (ascending) {
        "${label}-ascending"
    } else {
        "${label}-descending"
    }
    var lastPasses = 0
    var lastSwaps = 0
    public override func sort(values: ArrayList<Int64>): ArrayList<Int64> {
        let items = ArrayList<Int64>()
        for (value in values) {
            items.add(value)
        }
        lastPasses = 0
        lastSwaps = 0
        if (items.size <= 1) {
            return items
        }
        var end = items.size - 1
        while (end > 0) {
            var swapped = false
            var i = 0
            while (i < end) {
                let shouldSwap = if (ascending) {
                    items[i] > items[i + 1]
                } else {
                    items[i] < items[i + 1]
                }
                if (shouldSwap) {
                    items.swapAt(i, i + 1)
                    swapped = true
                    lastSwaps += 1
                }
                i += 1
            }
            lastPasses += 1
            if (!swapped) {
                break
            }
            end -= 1
        }
        return items
    }
    public override func describe(): String {
        return "Bubble sort compares adjacent values and bubbles extremes toward the edge"
    }
}

class SelectionSortStrategy <: SortStrategy {
    let ascending: Bool
    let label: String
    init(ascending!: Bool = true, label!: String = "selection") {
        this.ascending = ascending
        this.label = label
    }
    let strategyName: String = if (ascending) {
        "${label}-ascending"
    } else {
        "${label}-descending"
    }
    var lastPasses = 0
    var lastSwaps = 0
    public override func sort(values: ArrayList<Int64>): ArrayList<Int64> {
        let items = ArrayList<Int64>()
        for (value in values) {
            items.add(value)
        }
        lastPasses = 0
        lastSwaps = 0
        var start = 0
        while (start < items.size) {
            var selected = start
            var i = start + 1
            while (i < items.size) {
                let shouldPick = if (ascending) {
                    items[i] < items[selected]
                } else {
                    items[i] > items[selected]
                }
                if (shouldPick) {
                    selected = i
                }
                i += 1
            }
            if (selected != start) {
                items.swapAt(start, selected)
                lastSwaps += 1
            }
            lastPasses += 1
            start += 1
        }
        return items
    }
    public override func describe(): String {
        return "Selection sort scans the remaining suffix and places one chosen element per pass"
    }
}

class Sorter {
    init(initialStrategy: SortStrategy) {
    }
    var strategy: SortStrategy = initialStrategy
    let reports = ArrayList<SortReport>()
    func changeStrategy(next: SortStrategy) {
        strategy = next
    }
    func sort(values: ArrayList<Int64>): ArrayList<Int64> {
        return strategy.sort(values)
    }
    func sortAndRecord(values: ArrayList<Int64>): SortReport {
        let before = String.join(collectArray<String>(values.iterator().map({e => e.toString()})), delimiter: ", ")
        let result = strategy.sort(values)
        let after = String.join(collectArray<String>(result.iterator().map({e => e.toString()})), delimiter: ", ")
        let report = match (strategy) {
            case strategy: BubbleSortStrategy => 
                let bubble = (strategy as BubbleSortStrategy)
                SortReport(strategy.strategyName, before, after, bubble.lastPasses, bubble.lastSwaps)
            case strategy: SelectionSortStrategy => 
                let selection = (strategy as SelectionSortStrategy)
                SortReport(strategy.strategyName, before, after, selection.lastPasses, selection.lastSwaps)
            case _ => SortReport(strategy.strategyName, before, after, 0, 0)}
        reports.add(report)
        return report
    }
    func sortMany(listOfLists: ArrayList<ArrayList<Int64>>): ArrayList<ArrayList<Int64>> {
        let result = ArrayList<ArrayList<Int64>>()
        for (items in listOfLists) {
            result.add(sort(items))
        }
        return result
    }
    func reportLines(): ArrayList<String> {
        let lines = ArrayList<String>()
        for (report in reports) {
            lines.add("${report.strategyName}: [${report.before}] -> [${report.after}] passes=${report.passes} swaps=${report.swaps}")
        }
        return lines
    }
}

open class Expr {
    public func acceptEval(visitor: EvalVisitor): Int64
    public func acceptPrint(visitor: PrintVisitor): String
    public func acceptSimplify(visitor: SimplifyVisitor): Expr
}

class NumberExpr <: Expr & ToString {
    let value: Int64
    init(value: Int64) {
        this.value = value
    }
    public override func acceptEval(visitor: EvalVisitor): Int64 {
        return visitor.visitNumber(this)
    }
    public override func acceptPrint(visitor: PrintVisitor): String {
        return visitor.visitNumber(this)
    }
    public override func acceptSimplify(visitor: SimplifyVisitor): Expr {
        return visitor.visitNumber(this)
    }
    public func toString(): String {
        return "NumberExpr(value=${this.value})"
    }
}

class AddExpr <: Expr & ToString {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
    public override func acceptEval(visitor: EvalVisitor): Int64 {
        return visitor.visitAdd(this)
    }
    public override func acceptPrint(visitor: PrintVisitor): String {
        return visitor.visitAdd(this)
    }
    public override func acceptSimplify(visitor: SimplifyVisitor): Expr {
        return visitor.visitAdd(this)
    }
    public func toString(): String {
        return "AddExpr(left=${this.left}, right=${this.right})"
    }
}

class SubExpr <: Expr & ToString {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
    public override func acceptEval(visitor: EvalVisitor): Int64 {
        return visitor.visitSub(this)
    }
    public override func acceptPrint(visitor: PrintVisitor): String {
        return visitor.visitSub(this)
    }
    public override func acceptSimplify(visitor: SimplifyVisitor): Expr {
        return visitor.visitSub(this)
    }
    public func toString(): String {
        return "SubExpr(left=${this.left}, right=${this.right})"
    }
}

class MulExpr <: Expr & ToString {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
    public override func acceptEval(visitor: EvalVisitor): Int64 {
        return visitor.visitMul(this)
    }
    public override func acceptPrint(visitor: PrintVisitor): String {
        return visitor.visitMul(this)
    }
    public override func acceptSimplify(visitor: SimplifyVisitor): Expr {
        return visitor.visitMul(this)
    }
    public func toString(): String {
        return "MulExpr(left=${this.left}, right=${this.right})"
    }
}

class EvalVisitor {
    func visitNumber(expr: NumberExpr): Int64 {
        return expr.value
    }
    func visitAdd(expr: AddExpr): Int64 {
        return expr.left.acceptEval(this) + expr.right.acceptEval(this)
    }
    func visitSub(expr: SubExpr): Int64 {
        return expr.left.acceptEval(this) - expr.right.acceptEval(this)
    }
    func visitMul(expr: MulExpr): Int64 {
        return expr.left.acceptEval(this) * expr.right.acceptEval(this)
    }
}

class PrintVisitor {
    func visitNumber(expr: NumberExpr): String {
        return "${expr.value}"
    }
    func visitAdd(expr: AddExpr): String {
        return "(${expr.left.acceptPrint(this)} + ${expr.right.acceptPrint(this)})"
    }
    func visitSub(expr: SubExpr): String {
        return "(${expr.left.acceptPrint(this)} - ${expr.right.acceptPrint(this)})"
    }
    func visitMul(expr: MulExpr): String {
        return "(${expr.left.acceptPrint(this)} * ${expr.right.acceptPrint(this)})"
    }
}

class SimplifyVisitor {
    func visitNumber(expr: NumberExpr): Expr {
        return expr
    }
    func visitAdd(expr: AddExpr): Expr {
        let left = expr.left.acceptSimplify(this)
        let right = expr.right.acceptSimplify(this)
        if ((left is NumberExpr) && (right is NumberExpr)) {
            return NumberExpr(left.value + right.value)
        }
        if ((left is NumberExpr) && (left.value == 0)) {
            return right
        }
        if ((right is NumberExpr) && (right.value == 0)) {
            return left
        }
        return AddExpr(left, right)
    }
    func visitSub(expr: SubExpr): Expr {
        let left = expr.left.acceptSimplify(this)
        let right = expr.right.acceptSimplify(this)
        if ((left is NumberExpr) && (right is NumberExpr)) {
            return NumberExpr(left.value - right.value)
        }
        if ((right is NumberExpr) && (right.value == 0)) {
            return left
        }
        return SubExpr(left, right)
    }
    func visitMul(expr: MulExpr): Expr {
        let left = expr.left.acceptSimplify(this)
        let right = expr.right.acceptSimplify(this)
        if ((left is NumberExpr) && (right is NumberExpr)) {
            return NumberExpr(left.value * right.value)
        }
        if ((left is NumberExpr) && (left.value == 0)) {
            return NumberExpr(0)
        }
        if ((right is NumberExpr) && (right.value == 0)) {
            return NumberExpr(0)
        }
        if ((left is NumberExpr) && (left.value == 1)) {
            return right
        }
        if ((right is NumberExpr) && (right.value == 1)) {
            return left
        }
        return MulExpr(left, right)
    }
}

func summarizeExpression(expr: Expr): String {
    let eval = EvalVisitor()
    let printer = PrintVisitor()
    let simplifier = SimplifyVisitor()
    let simplified = expr.acceptSimplify(simplifier)
    return "expr=${expr.acceptPrint(printer)} value=${expr.acceptEval(eval)} simplified=${simplified.acceptPrint(printer)} simplifiedValue=${simplified.acceptEval(eval)}"
}

extend String {
    func manualUpper(): String {
        let builder = StringBuilder()
        var index = 0
        while (index < this.size) {
            let ch = this[index..index + 1]
            let replaced = match (ch) {
                case "a" => "A"
                case "b" => "B"
                case "c" => "C"
                case "d" => "D"
                case "e" => "E"
                case "f" => "F"
                case "g" => "G"
                case "h" => "H"
                case "i" => "I"
                case "j" => "J"
                case "k" => "K"
                case "l" => "L"
                case "m" => "M"
                case "n" => "N"
                case "o" => "O"
                case "p" => "P"
                case "q" => "Q"
                case "r" => "R"
                case "s" => "S"
                case "t" => "T"
                case "u" => "U"
                case "v" => "V"
                case "w" => "W"
                case "x" => "X"
                case "y" => "Y"
                case "z" => "Z"
                case _ => ch}
            builder.append(replaced)
            index += 1
        }
        return builder.toString()
    }
}

extend String {
    func manualLower(): String {
        let builder = StringBuilder()
        var index = 0
        while (index < this.size) {
            let ch = this[index..index + 1]
            let replaced = match (ch) {
                case "A" => "a"
                case "B" => "b"
                case "C" => "c"
                case "D" => "d"
                case "E" => "e"
                case "F" => "f"
                case "G" => "g"
                case "H" => "h"
                case "I" => "i"
                case "J" => "j"
                case "K" => "k"
                case "L" => "l"
                case "M" => "m"
                case "N" => "n"
                case "O" => "o"
                case "P" => "p"
                case "Q" => "q"
                case "R" => "r"
                case "S" => "s"
                case "T" => "t"
                case "U" => "u"
                case "V" => "v"
                case "W" => "w"
                case "X" => "x"
                case "Y" => "y"
                case "Z" => "z"
                case _ => ch}
            builder.append(replaced)
            index += 1
        }
        return builder.toString()
    }
}

func printSection(title: String) {
    println("=== ${title} ===")
}

func printSubSection(title: String) {
    println("--- ${title} ---")
}

func printLines(lines: ArrayList<String>) {
    for (line in lines) {
        println(line)
    }
}

func printListWithPrefix(prefix: String, values: ArrayList<String>) {
    var index = 0
    while (index < values.size) {
        println("${prefix}${index + 1}: ${values[index]}")
        index += 1
    }
}

func runObserverDemo() {
    printSection("Observer Pattern")
    let bus = EventBus("demo-bus")
    let acceptedMetrics = ArrayList<String>()
    let logger = LoggingListener("logger", "console")
    let counter = CountingListener("counter")
    let filter = FilteringListener("filter", "metric", acceptedMetrics)
    let audit = AuditListener("audit")
    bus.subscribe("metric", logger)
    bus.subscribe("metric", counter)
    bus.subscribe("metric", filter)
    bus.subscribe("alert", logger)
    bus.subscribe("alert", audit)
    bus.subscribe("status", counter)
    let busTopics = String.join(collectArray<String>(bus.topicNames().iterator().map({e => e.toString()})), delimiter: ", ")
    let metricListenerCount = bus.listenerCount("metric")
    let statusListenerCount = bus.listenerCount("status")
    let unknownListenerCount = bus.listenerCount("unknown")
    println("bus topics=${busTopics}")
    printLines(bus.describeSubscriptions())
    println("metric listeners=${metricListenerCount}")
    println("status listeners=${statusListenerCount}")
    println("unknown listeners=${unknownListenerCount}")
    printSubSection("publish round 1")
    let roundOne = ArrayList([Event("metric", "sensor-A", "temp=21", priority: 1), Event("metric", "sensor-B", "temp=19", priority: 2), Event("alert", "gateway", "battery low", priority: 5), Event("status", "gateway", "online", priority: 1), Event("unknown", "ghost", "shadow", priority: 9)])
    var eventIndex = 0
    while (eventIndex < roundOne.size) {
        let event = roundOne[eventIndex]
        println("event ${eventIndex + 1}: ${event.`type`}/${event.source}/${event.payload}/${event.priority}")
        printListWithPrefix("  message ", bus.publish(event))
        eventIndex += 1
    }
    printSubSection("unsubscribe and publish round 2")
    let removedFilter = bus.unsubscribe("metric", "filter")
    let removedGhost = bus.unsubscribe("metric", "ghost")
    println("unsubscribe filter from metric -> ${removedFilter}")
    println("unsubscribe ghost from metric -> ${removedGhost}")
    let roundTwo = ArrayList([Event("metric", "sensor-A", "temp=22", priority: 2), Event("alert", "gateway", "maintenance window", priority: 3), Event("status", "gateway", "offline", priority: 4)])
    for (event in roundTwo) {
        println("event ${event.`type`}/${event.source}/${event.payload}/${event.priority}")
        printListWithPrefix("  message ", bus.publish(event))
    }
    printSubSection("observer summaries")
    let acceptedMetricText = String.join(collectArray<String>(acceptedMetrics.iterator().map({e => e.toString()})), delimiter: ", ")
    println("accepted metrics=${acceptedMetricText}")
    println("logger handled=${logger.handledCount}")
    println("logger last=${logger.lastMessage()}")
    println("counter handled=${counter.handledCount}")
    println("counter types=${counter.typeSummary()}")
    println("counter sources=${counter.sourceSummary()}")
    println("filter handled=${filter.handledCount}")
    println("filter history=${filter.describeHistory()}")
    println("audit handled=${audit.handledCount}")
    println("audit history=${audit.describeHistory()}")
    println("publish log=${bus.publishSummary()}")
    println()
}

func printSortReport(report: SortReport) {
    println("strategy=${report.strategyName}")
    println("before=[${report.before}]")
    println("after=[${report.after}]")
    println("passes=${report.passes} swaps=${report.swaps}")
}

func runStrategyDemo() {
    printSection("Strategy Pattern")
    let bubbleAsc = BubbleSortStrategy(ascending: true, label: "bubble")
    let selectionDesc = SelectionSortStrategy(ascending: false, label: "selection")
    let selectionAsc = SelectionSortStrategy(ascending: true, label: "selection")
    let sorter = Sorter(bubbleAsc)
    let dataOne = ArrayList([9, 3, 7, 1, 7, 2])
    let dataTwo = ArrayList([4, 4, 8, 1, 0, 6])
    let dataThree = ArrayList([5, 2, 9, 2, 8])
    println("description1=${bubbleAsc.describe()}")
    println("description2=${selectionDesc.describe()}")
    printSubSection("single sorts")
    printSortReport(sorter.sortAndRecord(dataOne))
    sorter.changeStrategy(selectionDesc)
    printSortReport(sorter.sortAndRecord(dataTwo))
    sorter.changeStrategy(selectionAsc)
    printSortReport(sorter.sortAndRecord(dataThree))
    printSubSection("batch sort")
    sorter.changeStrategy(bubbleAsc)
    let batches = ArrayList([ArrayList([3, 1, 2]), ArrayList([10, 5, 10, 1]), ArrayList([8, 6])])
    let batchSorted = sorter.sortMany(batches)
    var batchIndex = 0
    while (batchIndex < batchSorted.size) {
        let batchText = String.join(collectArray<String>(batchSorted[batchIndex].iterator().map({e => e.toString()})), delimiter: ", ")
        println("batch ${batchIndex + 1} -> [${batchText}]")
        batchIndex += 1
    }
    printSubSection("collection calculations")
    let allNumbers = ArrayList<Int64>()
    for (value in dataOne) {
        allNumbers.add(value)
    }
    for (value in dataTwo) {
        allNumbers.add(value)
    }
    for (value in dataThree) {
        allNumbers.add(value)
    }
    let doubled = collectArrayList(allNumbers.iterator().map({ it => it * 2 }))
    let filtered = collectArrayList(allNumbers.iterator().filter({ it => it >= 5 }))
    let ordered = ({ => let _s = collectArrayList(allNumbers.iterator()); sort(_s, stable: true); _s })()
    let orderedByDistance = ({ => let _s = collectArrayList(allNumbers.iterator()); sort(_s, key: { it => (if (it > 5) { it } else { 5 }) - (if (it < 5) { it } else { 5 }) }, stable: true); _s })()
    let folded = allNumbers.iterator().fold<Int64>(10, { acc, item => acc + item })
    let reduced = filtered.iterator().reduce({ acc, item => acc + item }).getOrThrow()
    let countEven = allNumbers.iterator().filter({ it => (it % 2) == 0 }).count()
    let anyLarge = allNumbers.iterator().any({ it => it > 8 })
    let allPositive = allNumbers.iterator().all({ it => it >= 0 })
    let noneNegative = !allNumbers.iterator().any({ it => it < 0 })
    let sumNumbers = allNumbers.iterator().fold<Int64>(0, {acc, x => acc + x})
    let allNumbersText = String.join(collectArray<String>(allNumbers.iterator().map({e => e.toString()})), delimiter: ", ")
    let doubledText = String.join(collectArray<String>(doubled.iterator().map({e => e.toString()})), delimiter: ", ")
    let filteredText = String.join(collectArray<String>(filtered.iterator().map({e => e.toString()})), delimiter: ", ")
    let orderedText = String.join(collectArray<String>(ordered.iterator().map({e => e.toString()})), delimiter: ", ")
    let orderedByDistanceText = String.join(collectArray<String>(orderedByDistance.iterator().map({e => e.toString()})), delimiter: ", ")
    let reportText = String.join(collectArray<String>(sorter.reportLines().iterator().map({e => e.toString()})), delimiter: " || ")
    println("allNumbers=[${allNumbersText}]")
    println("doubled=[${doubledText}]")
    println("filtered>=5=[${filteredText}]")
    println("ordered=[${orderedText}]")
    println("orderedByDistance=[${orderedByDistanceText}]")
    println("folded=${folded}")
    println("reducedFiltered=${reduced}")
    println("countEven=${countEven} anyLarge=${anyLarge} allPositive=${allPositive} noneNegative=${noneNegative} sum=${sumNumbers}")
    println("reportLines=${reportText}")
    println()
}

func runFactoryDemo() {
    printSection("Factory Pattern")
    let factory = ShapeFactory()
    let specs = ShapeFactory.standardSpecs()
    specs.add(ShapeSpec("circle", 5))
    specs.add(ShapeSpec("rectangle", 2, second: 7))
    specs.add(ShapeSpec("triangle", 8, second: 6, third: 5))
    let shapes = factory.createBatch(specs)
    printSubSection("base shapes")
    var index = 0
    while (index < shapes.size) {
        let shape = shapes[index]
        println("shape ${index + 1}: ${shape.describe()}")
        println("  scaled x2 -> ${shape.scale(2).describe()}")
        index += 1
    }
    println("totalArea=${factory.totalArea(shapes)}")
    println("totalPerimeter=${factory.totalPerimeter(shapes)}")
    printSubSection("abstract factory showcases")
    let redFactory = ColoredShapeFactory("red")
    let blueFactory = ColoredShapeFactory("blue")
    let greenFactory = ColoredShapeFactory("green")
    let factories = ArrayList([redFactory, blueFactory, greenFactory])
    for (colorFactory in factories) {
        let showcase = colorFactory.buildShowcase()
        println("palette=${colorFactory.paletteName()}")
        println("summary=${colorFactory.summary(showcase)}")
        for (item in showcase) {
            println("  ${item.describe()}")
        }
    }
    printSubSection("direct colored creation")
    let purpleFactory = ColoredShapeFactory("purple")
    let directOne = purpleFactory.createColoredShape("circle", 6)
    let directTwo = purpleFactory.createColoredShape("triangle", 7, 4, 6)
    let directThree = purpleFactory.createColoredShape("hexagon", 1)
    let directOneText = directOne?.describe() ?? "null"
    let directTwoText = directTwo?.describe() ?? "null"
    let directThreeText = directThree?.describe() ?? "null"
    println("directOne=${directOneText}")
    println("directTwo=${directTwoText}")
    println("directThree=${directThreeText}")
    println()
}

func printCoffee(title: String, coffee: Coffee) {
    println(title)
    printLines(coffeeReceiptLines(coffee))
    let upperIngredients = collectArrayList(coffee.ingredients().iterator().map({ it => it.manualUpper() }))
    let sortedIngredients = ({ => let _s = collectArrayList(coffee.ingredients().iterator()); sort(_s, stable: true); _s })()
    let sugarCount = coffee.ingredients().iterator().filter({ it => it == "sugar" }).count()
    let upperIngredientText = String.join(collectArray<String>(upperIngredients.iterator().map({e => e.toString()})), delimiter: ", ")
    let sortedIngredientText = String.join(collectArray<String>(sortedIngredients.iterator().map({e => e.toString()})), delimiter: ", ")
    println("upperIngredients=${upperIngredientText}")
    println("sortedIngredients=${sortedIngredientText}")
    println("sugarCount=${sugarCount}")
}

func runDecoratorDemo() {
    printSection("Decorator Pattern")
    let coffeeOne = CoffeeBuilder(baseBean: "House Blend").addMilk(1).addSugar(2).build()
    let coffeeTwo = CoffeeBuilder(baseBean: "Dark Roast").addWhip(2).addMilk(2).build()
    let coffeeThree = CoffeeBuilder(baseBean: "Decaf").addSugar(1).addWhip(1).addMilk(1).build()
    printCoffee("order one", coffeeOne)
    printCoffee("order two", coffeeTwo)
    printCoffee("order three", coffeeThree)
    let totals = ArrayList([coffeeOne.cost(), coffeeTwo.cost(), coffeeThree.cost()])
    let totalText = String.join(collectArray<String>(totals.iterator().map({e => e.toString()})), delimiter: ", ")
    let totalMax = (if (totals[0] > (if (totals[1] > totals[2]) { totals[1] } else { totals[2] })) { totals[0] } else { (if (totals[1] > totals[2]) { totals[1] } else { totals[2] }) })
    let totalMin = (if (totals[0] < (if (totals[1] < totals[2]) { totals[1] } else { totals[2] })) { totals[0] } else { (if (totals[1] < totals[2]) { totals[1] } else { totals[2] }) })
    println("cost totals=[${totalText}] sum=${totals.iterator().fold<Int64>(0, {acc, x => acc + x})} max=${totalMax} min=${totalMin}")
    println()
}

func runCompositeDemo() {
    printSection("Composite Pattern")
    let root = DirectoryNode("root")
    let src = DirectoryNode("src")
    let docs = DirectoryNode("docs")
    let assets = DirectoryNode("assets")
    let nested = DirectoryNode("nested")
    src.add(FileNode("Main.kt", "fun main() = println(\"hi\")"))
    src.add(FileNode("Util.kt", "class Util { fun x() = 1 }"))
    docs.add(FileNode("README.md", "patterns and translators"))
    assets.add(FileNode("logo.txt", "***logo***"))
    nested.add(FileNode("notes.txt", "observer strategy factory decorator"))
    assets.add(nested)
    root.add(src)
    root.add(docs)
    root.add(assets)
    printSubSection("tree list")
    printLines(root.list())
    printSubSection("flattened paths")
    printLines(root.flatten())
    printSubSection("find operations")
    let findMain = root.find("Main.kt")
    let findNested = root.find("nested")
    let findGhost = root.find("ghost")
    let findMainKind = findMain?.kind() ?? "null"
    let findNestedKind = findNested?.kind() ?? "null"
    let findGhostKind = findGhost?.kind() ?? "null"
    let findMainSize = findMain?.size() ?? -1
    let findNestedSize = findNested?.size() ?? -1
    let rootCountBefore = root.countNodes()
    let rootSizeBefore = root.size()
    let assetChildrenBefore = String.join(collectArray<String>(assets.childNames().iterator().map({e => e.toString()})), delimiter: ", ")
    println("find Main.kt -> ${findMainKind} size=${findMainSize}")
    println("find nested -> ${findNestedKind} size=${findNestedSize}")
    println("find ghost -> ${findGhostKind}")
    println("root nodes=${rootCountBefore} size=${rootSizeBefore}")
    println("assets children=${assetChildrenBefore}")
    let removedLogo = assets.remove("logo.txt")
    let removedMissing = assets.remove("missing.bin")
    let assetChildrenAfter = String.join(collectArray<String>(assets.childNames().iterator().map({e => e.toString()})), delimiter: ", ")
    println("remove logo.txt -> ${removedLogo}")
    println("remove missing.bin -> ${removedMissing}")
    println("assets children after remove=${assetChildrenAfter}")
    println("root nodes after remove=${root.countNodes()} size=${root.size()}")
    println()
}

func runCommandDemo() {
    printSection("Command Pattern")
    let editor = TextEditor(initialText: "start")
    let commands = ArrayList<Command>([InsertCommand(editor, 5, "-here"), ReplaceCommand(editor, "start", "BEGIN", replaceAll: false), InsertCommand(editor, 0, "("), InsertCommand(editor, editor.text.size, ")"), DeleteCommand(editor, 6, 2), ReplaceCommand(editor, "e", "E", replaceAll: true)])
    printSubSection("execute commands")
    var index = 0
    while (index < commands.size) {
        let command = commands[index]
        println("command ${index + 1}: ${command.describe()}")
        println("  result=${editor.executeCommand(command)}")
        println("  text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
        index += 1
    }
    printSubSection("undo sequence")
    println(editor.undo())
    println("text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
    println(editor.undo())
    println("text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
    println(editor.undo())
    println("text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
    printSubSection("redo sequence")
    println(editor.redo())
    println("text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
    println(editor.redo())
    println("text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
    printSubSection("extra command after redo clear")
    let extra = InsertCommand(editor, editor.text.size, "!")
    println(editor.executeCommand(extra))
    println("text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
    println(editor.redo())
    println("text=${editor.snapshot()} undo=${editor.historySize()} redo=${editor.redoSize()}")
    printSubSection("timeline")
    for (line in editor.timeline) {
        println(line)
    }
    println()
}

func runStateDemo() {
    printSection("State Pattern")
    let machine = VendingMachine()
    println("initial=${machine.status()}")
    println(machine.select(Product.WATER))
    println("status=${machine.status()}")
    println(machine.insertCoin(2))
    println("status=${machine.status()}")
    println(machine.select(Product.WATER))
    println("status=${machine.status()}")
    println(machine.insertCoin(2))
    println("status=${machine.status()}")
    println(machine.select(Product.WATER))
    println("status=${machine.status()}")
    println(machine.finishDispense())
    println("status=${machine.status()}")
    println(machine.insertCoin(5))
    println(machine.select(Product.JUICE))
    println(machine.finishDispense())
    println(machine.insertCoin(3))
    println(machine.select(Product.JUICE))
    println(machine.refund())
    println(machine.insertCoin(4))
    println(machine.select(Product.TEA))
    println(machine.finishDispense())
    println(machine.refund())
    println("final=${machine.status()}")
    printSubSection("audit")
    printLines(machine.auditLines())
    println()
}

func runVisitorDemo() {
    printSection("Visitor Pattern")
    let exprOne = AddExpr(NumberExpr(2), MulExpr(NumberExpr(3), NumberExpr(4)))
    let exprTwo = MulExpr(AddExpr(NumberExpr(0), NumberExpr(5)), NumberExpr(1))
    let exprThree = SubExpr(MulExpr(NumberExpr(10), NumberExpr(2)), AddExpr(NumberExpr(3), NumberExpr(7)))
    let exprFour = AddExpr(SubExpr(NumberExpr(8), NumberExpr(8)), MulExpr(NumberExpr(0), NumberExpr(9)))
    let expressions = ArrayList([exprOne, exprTwo, exprThree, exprFour])
    var index = 0
    while (index < expressions.size) {
        println("expression ${index + 1}: ${summarizeExpression(expressions[index])}")
        index += 1
    }
    let printer = PrintVisitor()
    let eval = EvalVisitor()
    let simplifier = SimplifyVisitor()
    let simplifiedStrings = collectArrayList(expressions.iterator().map({ it => it.acceptSimplify(simplifier).acceptPrint(printer) }))
    let values = collectArrayList(expressions.iterator().map({ it => it.acceptEval(eval) }))
    let simplifiedText = String.join(collectArray<String>(simplifiedStrings.iterator().map({e => e.toString()})), delimiter: ", ")
    let valuesText = String.join(collectArray<String>(values.iterator().map({e => e.toString()})), delimiter: ", ")
    let valueMax = (if ((if (values[0] > values[1]) { values[0] } else { values[1] }) > (if (values[2] > values[3]) { values[2] } else { values[3] })) { (if (values[0] > values[1]) { values[0] } else { values[1] }) } else { (if (values[2] > values[3]) { values[2] } else { values[3] }) })
    let valueMin = (if ((if (values[0] < values[1]) { values[0] } else { values[1] }) < (if (values[2] < values[3]) { values[2] } else { values[3] })) { (if (values[0] < values[1]) { values[0] } else { values[1] }) } else { (if (values[2] < values[3]) { values[2] } else { values[3] }) })
    println("simplifiedStrings=${simplifiedText}")
    println("values=${valuesText} sum=${values.iterator().fold<Int64>(0, {acc, x => acc + x})} max=${valueMax} min=${valueMin}")
    println()
}

func runChainDemo() {
    printSection("Chain Of Responsibility Pattern")
    let console = ConsoleLogger("console", LogLevel.DEBUG)
    let file = FileLogger("file", LogLevel.INFO)
    let error = ErrorLogger("error", LogLevel.ERROR)
    console.setNext(file).setNext(error)
    let messages = ArrayList([LogMessage(LogLevel.DEBUG, "boot", "starting"), LogMessage(LogLevel.INFO, "auth", "login ok"), LogMessage(LogLevel.WARN, "disk", "usage 85"), LogMessage(LogLevel.ERROR, "db", "connection lost")])
    var index = 0
    while (index < messages.size) {
        let message = messages[index]
        println("message ${index + 1}: ${message.level}/${message.channel}/${message.text}")
        printListWithPrefix("  chain ", console.log(message))
        index += 1
    }
    printSubSection("logger summaries")
    println(console.summary())
    println(file.summary())
    println(error.summary())
    println()
}

func runStringAndBuilderExtras() {
    printSection("Translator Friendly Extras")
    let raw = "  Kotlin To Cangjie Patterns  "
    let trimmed = raw.trimAscii()
    let replaced = trimmed.replace(" ", "-")
    let lower = trimmed.manualLower()
    let upper = trimmed.manualUpper()
    let parts = collectArrayList(trimmed.split(" ").iterator())
    let containsWord = trimmed.contains("Cangjie")
    let startsWord = trimmed.startsWith("Kotlin")
    let endsWord = trimmed.endsWith("Patterns")
    let partsText = String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: ", ")
    println("raw='${raw}'")
    println("trimmed='${trimmed}'")
    println("replaced='${replaced}'")
    println("lower='${lower}'")
    println("upper='${upper}'")
    println("contains='${containsWord}' starts='${startsWord}' ends='${endsWord}' length=${trimmed.size}")
    println("parts=${partsText}")
    let builder = StringBuilder()
    builder.append("observer")
    builder.append("|")
    builder.append("strategy")
    builder.append("|")
    builder.append("factory")
    println("builder=${builder}")
    let nullableText: ?String = if (trimmed.size > 0) {
        trimmed
    } else {
        None
    }
    let safeLength = nullableText?.size ?? -1
    let forced = nullableText.getOrThrow()[0..6]
    println("nullableText=${nullableText} safeLength=${safeLength} forced=${forced}")
    let containerA = NamedBox("patterns", 3)
    let containerB = NamedBox("visitors", 7)
    println("boxA=${containerA.describe()}")
    println("boxB=${containerB.describe()}")
    println()
}

class NamedBox<T> {
    let name: String
    let value: T
    init(name: String, value: T) {
        this.name = name
        this.value = value
    }
    func describe(): String {
        return "${name}=>${value}"
    }
}

main() {
    println("PROJECT proj_patterns START")
    println()
    runObserverDemo()
    runStrategyDemo()
    runFactoryDemo()
    runDecoratorDemo()
    runCompositeDemo()
    runCommandDemo()
    runStateDemo()
    runVisitorDemo()
    runChainDemo()
    runStringAndBuilderExtras()
    println("PROJECT proj_patterns END")
}
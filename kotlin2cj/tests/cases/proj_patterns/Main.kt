fun String.manualUpper(): String {
    val builder = StringBuilder()
    var index = 0
    while (index < this.length) {
        val ch = this.substring(index, index + 1)
        val replaced = when (ch) {
            "a" -> "A"
            "b" -> "B"
            "c" -> "C"
            "d" -> "D"
            "e" -> "E"
            "f" -> "F"
            "g" -> "G"
            "h" -> "H"
            "i" -> "I"
            "j" -> "J"
            "k" -> "K"
            "l" -> "L"
            "m" -> "M"
            "n" -> "N"
            "o" -> "O"
            "p" -> "P"
            "q" -> "Q"
            "r" -> "R"
            "s" -> "S"
            "t" -> "T"
            "u" -> "U"
            "v" -> "V"
            "w" -> "W"
            "x" -> "X"
            "y" -> "Y"
            "z" -> "Z"
            else -> ch
        }
        builder.append(replaced)
        index += 1
    }
    return builder.toString()
}

fun String.manualLower(): String {
    val builder = StringBuilder()
    var index = 0
    while (index < this.length) {
        val ch = this.substring(index, index + 1)
        val replaced = when (ch) {
            "A" -> "a"
            "B" -> "b"
            "C" -> "c"
            "D" -> "d"
            "E" -> "e"
            "F" -> "f"
            "G" -> "g"
            "H" -> "h"
            "I" -> "i"
            "J" -> "j"
            "K" -> "k"
            "L" -> "l"
            "M" -> "m"
            "N" -> "n"
            "O" -> "o"
            "P" -> "p"
            "Q" -> "q"
            "R" -> "r"
            "S" -> "s"
            "T" -> "t"
            "U" -> "u"
            "V" -> "v"
            "W" -> "w"
            "X" -> "x"
            "Y" -> "y"
            "Z" -> "z"
            else -> ch
        }
        builder.append(replaced)
        index += 1
    }
    return builder.toString()
}

fun printSection(title: String) {
    println("=== $title ===")
}

fun printSubSection(title: String) {
    println("--- $title ---")
}

fun printLines(lines: MutableList<String>) {
    for (line in lines) {
        println(line)
    }
}

fun printListWithPrefix(prefix: String, values: MutableList<String>) {
    var index = 0
    while (index < values.size) {
        println("$prefix${index + 1}: ${values[index]}")
        index += 1
    }
}

fun runObserverDemo() {
    printSection("Observer Pattern")

    val bus = EventBus("demo-bus")
    val acceptedMetrics = mutableListOf<String>()
    val logger = LoggingListener("logger", "console")
    val counter = CountingListener("counter")
    val filter = FilteringListener("filter", "metric", acceptedMetrics)
    val audit = AuditListener("audit")

    bus.subscribe("metric", logger)
    bus.subscribe("metric", counter)
    bus.subscribe("metric", filter)
    bus.subscribe("alert", logger)
    bus.subscribe("alert", audit)
    bus.subscribe("status", counter)

    val busTopics = bus.topicNames().joinToString(", ")
    val metricListenerCount = bus.listenerCount("metric")
    val statusListenerCount = bus.listenerCount("status")
    val unknownListenerCount = bus.listenerCount("unknown")
    println("bus topics=$busTopics")
    printLines(bus.describeSubscriptions())
    println("metric listeners=$metricListenerCount")
    println("status listeners=$statusListenerCount")
    println("unknown listeners=$unknownListenerCount")

    printSubSection("publish round 1")
    val roundOne = mutableListOf(
        Event("metric", "sensor-A", "temp=21", 1),
        Event("metric", "sensor-B", "temp=19", 2),
        Event("alert", "gateway", "battery low", 5),
        Event("status", "gateway", "online", 1),
        Event("unknown", "ghost", "shadow", 9)
    )
    var eventIndex = 0
    while (eventIndex < roundOne.size) {
        val event = roundOne[eventIndex]
        println("event ${eventIndex + 1}: ${event.type}/${event.source}/${event.payload}/${event.priority}")
        printListWithPrefix("  message ", bus.publish(event))
        eventIndex += 1
    }

    printSubSection("unsubscribe and publish round 2")
    val removedFilter = bus.unsubscribe("metric", "filter")
    val removedGhost = bus.unsubscribe("metric", "ghost")
    println("unsubscribe filter from metric -> $removedFilter")
    println("unsubscribe ghost from metric -> $removedGhost")
    val roundTwo = mutableListOf(
        Event("metric", "sensor-A", "temp=22", 2),
        Event("alert", "gateway", "maintenance window", 3),
        Event("status", "gateway", "offline", 4)
    )
    for (event in roundTwo) {
        println("event ${event.type}/${event.source}/${event.payload}/${event.priority}")
        printListWithPrefix("  message ", bus.publish(event))
    }

    printSubSection("observer summaries")
    val acceptedMetricText = acceptedMetrics.joinToString(", ")
    println("accepted metrics=$acceptedMetricText")
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

fun printSortReport(report: SortReport) {
    println("strategy=${report.strategyName}")
    println("before=[${report.before}]")
    println("after=[${report.after}]")
    println("passes=${report.passes} swaps=${report.swaps}")
}

fun runStrategyDemo() {
    printSection("Strategy Pattern")

    val bubbleAsc = BubbleSortStrategy(true, "bubble")
    val selectionDesc = SelectionSortStrategy(false, "selection")
    val selectionAsc = SelectionSortStrategy(true, "selection")
    val sorter = Sorter(bubbleAsc)

    val dataOne = mutableListOf(9, 3, 7, 1, 7, 2)
    val dataTwo = mutableListOf(4, 4, 8, 1, 0, 6)
    val dataThree = mutableListOf(5, 2, 9, 2, 8)

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
    val batches = mutableListOf(
        mutableListOf(3, 1, 2),
        mutableListOf(10, 5, 10, 1),
        mutableListOf(8, 6)
    )
    val batchSorted = sorter.sortMany(batches)
    var batchIndex = 0
    while (batchIndex < batchSorted.size) {
        val batchText = batchSorted[batchIndex].joinToString(", ")
        println("batch ${batchIndex + 1} -> [$batchText]")
        batchIndex += 1
    }

    printSubSection("collection calculations")
    val allNumbers = mutableListOf<Int>()
    for (value in dataOne) {
        allNumbers.add(value)
    }
    for (value in dataTwo) {
        allNumbers.add(value)
    }
    for (value in dataThree) {
        allNumbers.add(value)
    }
    val doubled = allNumbers.map { it * 2 }
    val filtered = allNumbers.filter { it >= 5 }
    val ordered = allNumbers.sorted()
    val orderedByDistance = allNumbers.sortedBy { maxOf(it, 5) - minOf(it, 5) }
    val folded = allNumbers.fold(10) { acc, item -> acc + item }
    val reduced = filtered.reduce { acc, item -> acc + item }
    val countEven = allNumbers.count { it % 2 == 0 }
    val anyLarge = allNumbers.any { it > 8 }
    val allPositive = allNumbers.all { it >= 0 }
    val noneNegative = allNumbers.none { it < 0 }
    val sumNumbers = allNumbers.sum()
    val allNumbersText = allNumbers.joinToString(", ")
    val doubledText = doubled.joinToString(", ")
    val filteredText = filtered.joinToString(", ")
    val orderedText = ordered.joinToString(", ")
    val orderedByDistanceText = orderedByDistance.joinToString(", ")
    val reportText = sorter.reportLines().joinToString(" || ")
    println("allNumbers=[$allNumbersText]")
    println("doubled=[$doubledText]")
    println("filtered>=5=[$filteredText]")
    println("ordered=[$orderedText]")
    println("orderedByDistance=[$orderedByDistanceText]")
    println("folded=$folded")
    println("reducedFiltered=$reduced")
    println("countEven=$countEven anyLarge=$anyLarge allPositive=$allPositive noneNegative=$noneNegative sum=$sumNumbers")
    println("reportLines=$reportText")
    println()
}

fun runFactoryDemo() {
    printSection("Factory Pattern")

    val factory = ShapeFactory()
    val specs = ShapeFactory.standardSpecs()
    specs.add(ShapeSpec("circle", 5))
    specs.add(ShapeSpec("rectangle", 2, 7))
    specs.add(ShapeSpec("triangle", 8, 6, 5))
    val shapes = factory.createBatch(specs)

    printSubSection("base shapes")
    var index = 0
    while (index < shapes.size) {
        val shape = shapes[index]
        println("shape ${index + 1}: ${shape.describe()}")
        println("  scaled x2 -> ${shape.scale(2).describe()}")
        index += 1
    }
    println("totalArea=${factory.totalArea(shapes)}")
    println("totalPerimeter=${factory.totalPerimeter(shapes)}")

    printSubSection("abstract factory showcases")
    val redFactory = ColoredShapeFactory("red")
    val blueFactory = ColoredShapeFactory("blue")
    val greenFactory = ColoredShapeFactory("green")
    val factories = mutableListOf(redFactory, blueFactory, greenFactory)
    for (colorFactory in factories) {
        val showcase = colorFactory.buildShowcase()
        println("palette=${colorFactory.paletteName()}")
        println("summary=${colorFactory.summary(showcase)}")
        for (item in showcase) {
            println("  ${item.describe()}")
        }
    }

    printSubSection("direct colored creation")
    val purpleFactory = ColoredShapeFactory("purple")
    val directOne = purpleFactory.createColoredShape("circle", 6)
    val directTwo = purpleFactory.createColoredShape("triangle", 7, 4, 6)
    val directThree = purpleFactory.createColoredShape("hexagon", 1)
    val directOneText = directOne?.describe() ?: "null"
    val directTwoText = directTwo?.describe() ?: "null"
    val directThreeText = directThree?.describe() ?: "null"
    println("directOne=$directOneText")
    println("directTwo=$directTwoText")
    println("directThree=$directThreeText")
    println()
}

fun printCoffee(title: String, coffee: Coffee) {
    println(title)
    printLines(coffeeReceiptLines(coffee))
    val upperIngredients = coffee.ingredients().map { it.manualUpper() }
    val sortedIngredients = coffee.ingredients().sorted()
    val sugarCount = coffee.ingredients().count { it == "sugar" }
    val upperIngredientText = upperIngredients.joinToString(", ")
    val sortedIngredientText = sortedIngredients.joinToString(", ")
    println("upperIngredients=$upperIngredientText")
    println("sortedIngredients=$sortedIngredientText")
    println("sugarCount=$sugarCount")
}

fun runDecoratorDemo() {
    printSection("Decorator Pattern")

    val coffeeOne = CoffeeBuilder("House Blend").addMilk(1).addSugar(2).build()
    val coffeeTwo = CoffeeBuilder("Dark Roast").addWhip(2).addMilk(2).build()
    val coffeeThree = CoffeeBuilder("Decaf").addSugar(1).addWhip(1).addMilk(1).build()

    printCoffee("order one", coffeeOne)
    printCoffee("order two", coffeeTwo)
    printCoffee("order three", coffeeThree)

    val totals = mutableListOf(coffeeOne.cost(), coffeeTwo.cost(), coffeeThree.cost())
    val totalText = totals.joinToString(", ")
    val totalMax = maxOf(totals[0], maxOf(totals[1], totals[2]))
    val totalMin = minOf(totals[0], minOf(totals[1], totals[2]))
    println("cost totals=[$totalText] sum=${totals.sum()} max=$totalMax min=$totalMin")
    println()
}

fun runCompositeDemo() {
    printSection("Composite Pattern")

    val root = DirectoryNode("root")
    val src = DirectoryNode("src")
    val docs = DirectoryNode("docs")
    val assets = DirectoryNode("assets")
    val nested = DirectoryNode("nested")

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
    val findMain = root.find("Main.kt")
    val findNested = root.find("nested")
    val findGhost = root.find("ghost")
    val findMainKind = findMain?.kind() ?: "null"
    val findNestedKind = findNested?.kind() ?: "null"
    val findGhostKind = findGhost?.kind() ?: "null"
    val findMainSize = findMain?.size() ?: -1
    val findNestedSize = findNested?.size() ?: -1
    val rootCountBefore = root.countNodes()
    val rootSizeBefore = root.size()
    val assetChildrenBefore = assets.childNames().joinToString(", ")
    println("find Main.kt -> $findMainKind size=$findMainSize")
    println("find nested -> $findNestedKind size=$findNestedSize")
    println("find ghost -> $findGhostKind")
    println("root nodes=$rootCountBefore size=$rootSizeBefore")
    println("assets children=$assetChildrenBefore")
    val removedLogo = assets.remove("logo.txt")
    val removedMissing = assets.remove("missing.bin")
    val assetChildrenAfter = assets.childNames().joinToString(", ")
    println("remove logo.txt -> $removedLogo")
    println("remove missing.bin -> $removedMissing")
    println("assets children after remove=$assetChildrenAfter")
    println("root nodes after remove=${root.countNodes()} size=${root.size()}")
    println()
}

fun runCommandDemo() {
    printSection("Command Pattern")

    val editor = TextEditor("start")
    val commands = mutableListOf<Command>(
        InsertCommand(editor, 5, "-here"),
        ReplaceCommand(editor, "start", "BEGIN", false),
        InsertCommand(editor, 0, "("),
        InsertCommand(editor, editor.text.length, ")"),
        DeleteCommand(editor, 6, 2),
        ReplaceCommand(editor, "e", "E", true)
    )

    printSubSection("execute commands")
    var index = 0
    while (index < commands.size) {
        val command = commands[index]
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
    val extra = InsertCommand(editor, editor.text.length, "!")
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

fun runStateDemo() {
    printSection("State Pattern")

    val machine = VendingMachine()
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

fun runVisitorDemo() {
    printSection("Visitor Pattern")

    val exprOne = AddExpr(NumberExpr(2), MulExpr(NumberExpr(3), NumberExpr(4)))
    val exprTwo = MulExpr(AddExpr(NumberExpr(0), NumberExpr(5)), NumberExpr(1))
    val exprThree = SubExpr(MulExpr(NumberExpr(10), NumberExpr(2)), AddExpr(NumberExpr(3), NumberExpr(7)))
    val exprFour = AddExpr(SubExpr(NumberExpr(8), NumberExpr(8)), MulExpr(NumberExpr(0), NumberExpr(9)))
    val expressions = mutableListOf(exprOne, exprTwo, exprThree, exprFour)

    var index = 0
    while (index < expressions.size) {
        println("expression ${index + 1}: ${summarizeExpression(expressions[index])}")
        index += 1
    }

    val printer = PrintVisitor()
    val eval = EvalVisitor()
    val simplifier = SimplifyVisitor()
    val simplifiedStrings = expressions.map { it.acceptSimplify(simplifier).acceptPrint(printer) }
    val values = expressions.map { it.acceptEval(eval) }
    val simplifiedText = simplifiedStrings.joinToString(", ")
    val valuesText = values.joinToString(", ")
    val valueMax = maxOf(maxOf(values[0], values[1]), maxOf(values[2], values[3]))
    val valueMin = minOf(minOf(values[0], values[1]), minOf(values[2], values[3]))
    println("simplifiedStrings=$simplifiedText")
    println("values=$valuesText sum=${values.sum()} max=$valueMax min=$valueMin")
    println()
}

fun runChainDemo() {
    printSection("Chain Of Responsibility Pattern")

    val console = ConsoleLogger("console", LogLevel.DEBUG)
    val file = FileLogger("file", LogLevel.INFO)
    val error = ErrorLogger("error", LogLevel.ERROR)
    console.setNext(file).setNext(error)

    val messages = mutableListOf(
        LogMessage(LogLevel.DEBUG, "boot", "starting"),
        LogMessage(LogLevel.INFO, "auth", "login ok"),
        LogMessage(LogLevel.WARN, "disk", "usage 85"),
        LogMessage(LogLevel.ERROR, "db", "connection lost")
    )

    var index = 0
    while (index < messages.size) {
        val message = messages[index]
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

fun runStringAndBuilderExtras() {
    printSection("Translator Friendly Extras")

    val raw = "  Kotlin To Cangjie Patterns  "
    val trimmed = raw.trim()
    val replaced = trimmed.replace(" ", "-")
    val lower = trimmed.manualLower()
    val upper = trimmed.manualUpper()
    val parts = trimmed.split(" ")
    val containsWord = trimmed.contains("Cangjie")
    val startsWord = trimmed.startsWith("Kotlin")
    val endsWord = trimmed.endsWith("Patterns")
    val partsText = parts.joinToString(", ")
    println("raw='$raw'")
    println("trimmed='$trimmed'")
    println("replaced='$replaced'")
    println("lower='$lower'")
    println("upper='$upper'")
    println("contains='$containsWord' starts='$startsWord' ends='$endsWord' length=${trimmed.length}")
    println("parts=$partsText")

    val builder = StringBuilder()
    builder.append("observer")
    builder.append("|")
    builder.append("strategy")
    builder.append("|")
    builder.append("factory")
    println("builder=$builder")

    val nullableText: String? = if (trimmed.length > 0) trimmed else null
    val safeLength = nullableText?.length ?: -1
    val forced = nullableText!!.substring(0, 6)
    println("nullableText=$nullableText safeLength=$safeLength forced=$forced")

    val containerA = NamedBox("patterns", 3)
    val containerB = NamedBox("visitors", 7)
    println("boxA=${containerA.describe()}")
    println("boxB=${containerB.describe()}")
    println()
}

class NamedBox<T>(val name: String, val value: T) {
    fun describe(): String {
        return "$name=>$value"
    }
}

fun main() {
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

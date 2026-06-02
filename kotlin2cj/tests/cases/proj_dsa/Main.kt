data class SortScenario(val name: String, val values: ArrayList<Int>)

enum class DemoSection(val title: String) {
    LINKED_LIST("LinkedList Demo"),
    STACK("Stack Demo"),
    QUEUE("Queue Demo"),
    BST("BinarySearchTree Demo"),
    SORTING("Sorting Demo"),
    GRAPH("Graph Demo"),
    HASH_TABLE("HashTable Demo"),
    PRIORITY_QUEUE("PriorityQueue Demo"),
    SUMMARY("Project Summary")
}

data class DemoResult(val section: String, val checks: Int)

fun LinkedList<Int>.sumValues(): Int {
    var total = 0
    for (value in this.toArrayList()) {
        total += value
    }
    return total
}

fun ArrayList<Int>.pipeJoined(): String {
    return this.joinToString(" | ")
}

fun printSection(section: DemoSection) {
    println("")
    println("=== ${section.title} ===")
}

fun demoLinkedList(): DemoResult {
    printSection(DemoSection.LINKED_LIST)

    val list = LinkedList<Int>()
    println("Initial list: $list")
    println("Initially empty: ${list.isEmpty()}")

    list.addFirst(3)
    list.addFirst(2)
    list.addLast(5)
    list.addAt(2, 4)
    list.addAt(0, 1)
    println("After inserts: $list")
    println("Join with pipes: ${list.toArrayList().pipeJoined()}")
    println("Size after inserts: ${list.size()}")
    println("Contains 4: ${list.contains(4)}")
    println("Contains 9: ${list.contains(9)}")
    println("Find 5 -> ${list.find(5)?.value}")
    println("Index of 4: ${list.indexOf(4)}")
    println("Value at index 3: ${list.get(3)}")

    val replaced = list.set(3, 40)
    println("Set index 3 to 40: $replaced")
    println("After set: $list")
    println("List sum: ${list.sumValues()}")

    val removedFirst = list.removeFirst()
    val removedLast = list.removeLast()
    println("Removed first: $removedFirst")
    println("Removed last: $removedLast")
    println("After end removals: $list")

    val removedValue = list.remove(40)
    println("Removed value 40: $removedValue")
    println("After removing 40: $list")

    list.addLast(7)
    list.addLast(8)
    list.addAt(1, 9)
    println("After more inserts: $list")

    val removedAt = list.removeAt(2)
    println("Removed at index 2: $removedAt")
    println("Before reverse: $list")
    list.reverse()
    println("After reverse: $list")
    println("As array list: ${list.toArrayList()}")

    val copied = list.copy()
    copied.addLast(99)
    println("Copied list changed: $copied")
    println("Original remains: $list")

    list.clear()
    println("After clear: $list")
    println("Size after clear: ${list.size()}")
    println("Empty after clear: ${list.isEmpty()}")

    return DemoResult(DemoSection.LINKED_LIST.title, 18)
}

fun demoStack(): DemoResult {
    printSection(DemoSection.STACK)

    val stack = Stack<String>()
    println("Initial stack: $stack")
    println("Initially empty: ${stack.isEmpty()}")

    stack.push("red")
    stack.push("green")
    stack.push("blue")
    println("After pushes: $stack")
    println("Peek: ${stack.peek()}")
    println("Contains green: ${stack.contains("green")}")
    println("Contains black: ${stack.contains("black")}")

    val extra = ArrayList<String>()
    extra.add("white")
    extra.add("gold")
    stack.pushAll(extra)
    println("After pushAll: $stack")
    println("Reverse copy: ${stack.reverseCopy()}")
    println("Size: ${stack.size()}")

    println("Pop 1: ${stack.pop()}")
    println("Pop 2: ${stack.pop()}")
    println("Stack now: $stack")
    println("As array list: ${stack.toArrayList()}")
    println("Peek after pops: ${stack.peek()}")

    stack.clear()
    println("After clear: $stack")
    println("Empty after clear: ${stack.isEmpty()}")
    println("Pop on empty: ${stack.pop()}")

    return DemoResult(DemoSection.STACK.title, 12)
}

fun demoQueue(): DemoResult {
    printSection(DemoSection.QUEUE)

    val queue = Queue<Int>()
    println("Initial queue: $queue")
    println("Initially empty: ${queue.isEmpty()}")

    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)
    println("After enqueues: $queue")
    println("Peek: ${queue.peek()}")
    println("Contains 20: ${queue.contains(20)}")
    println("Contains 99: ${queue.contains(99)}")

    val more = ArrayList<Int>()
    more.add(40)
    more.add(50)
    queue.enqueueAll(more)
    println("After enqueueAll: $queue")

    println("Dequeue 1: ${queue.dequeue()}")
    println("Dequeue 2: ${queue.dequeue()}")
    println("Queue now: $queue")

    queue.rotate()
    println("After rotate: $queue")
    println("As array list: ${queue.toArrayList()}")
    println("Size: ${queue.size()}")

    queue.clear()
    println("After clear: $queue")
    println("Empty after clear: ${queue.isEmpty()}")
    println("Dequeue on empty: ${queue.dequeue()}")

    return DemoResult(DemoSection.QUEUE.title, 11)
}

fun demoBinarySearchTree(): DemoResult {
    printSection(DemoSection.BST)

    val tree = BinarySearchTree()
    val values = ArrayList<Int>()
    values.add(50)
    values.add(30)
    values.add(70)
    values.add(20)
    values.add(40)
    values.add(60)
    values.add(80)
    values.add(35)
    values.add(45)
    values.add(65)
    tree.insertAll(values)

    println("Tree inorder: ${tree.inorder()}")
    println("Tree preorder: ${tree.preorder()}")
    println("Tree postorder: ${tree.postorder()}")
    println("Tree level order: ${tree.levelOrder()}")
    println("Contains 45: ${tree.contains(45)}")
    println("Contains 99: ${tree.contains(99)}")
    println("Search 60 -> ${tree.search(60)?.value}")
    println("Min value: ${tree.min()}")
    println("Max value: ${tree.max()}")
    println("Height: ${tree.height()}")
    println("Leaf count: ${tree.countLeaves()}")
    println("Size: ${tree.size()}")
    println("Sum: ${tree.sum()}")

    println("Delete leaf 20: ${tree.delete(20)}")
    println("Inorder after deleting 20: ${tree.inorder()}")
    println("Delete one-child node 60: ${tree.delete(60)}")
    println("Inorder after deleting 60: ${tree.inorder()}")
    println("Delete two-child node 30: ${tree.delete(30)}")
    println("Inorder after deleting 30: ${tree.inorder()}")
    println("Delete missing 999: ${tree.delete(999)}")
    println("Level order after deletions: ${tree.levelOrder()}")
    println("Height after deletions: ${tree.height()}")
    println("Leaf count after deletions: ${tree.countLeaves()}")
    println("Sum after deletions: ${tree.sum()}")

    tree.clear()
    println("After clear inorder: ${tree.inorder()}")
    println("Empty after clear: ${tree.isEmpty()}")

    return DemoResult(DemoSection.BST.title, 18)
}

fun printSortResult(sorter: BaseSorter, scenario: SortScenario) {
    val sorted = sorter.sort(scenario.values)
    println("${sorter.name()} on ${scenario.name}: ${sorted}")
    println("${sorter.name()} sorted check: ${sorter.isSorted(sorted)}")
}

fun demoSorting(): DemoResult {
    printSection(DemoSection.SORTING)

    val scenarioAValues = ArrayList<Int>()
    scenarioAValues.add(9)
    scenarioAValues.add(4)
    scenarioAValues.add(7)
    scenarioAValues.add(1)
    scenarioAValues.add(3)
    scenarioAValues.add(8)
    scenarioAValues.add(2)
    val scenarioA = SortScenario("scenarioA", scenarioAValues)

    val scenarioBValues = ArrayList<Int>()
    scenarioBValues.add(5)
    scenarioBValues.add(1)
    scenarioBValues.add(5)
    scenarioBValues.add(2)
    scenarioBValues.add(9)
    scenarioBValues.add(2)
    scenarioBValues.add(0)
    val scenarioB = SortScenario("scenarioB", scenarioBValues)

    println("Original scenarioA: ${scenarioA.values}")
    println("Original scenarioB: ${scenarioB.values}")

    val bubble = BubbleSort()
    val insertion = InsertionSort()
    val selection = SelectionSort()
    val merge = MergeSort()
    val quick = QuickSort()

    printSortResult(bubble, scenarioA)
    printSortResult(bubble, scenarioB)
    printSortResult(insertion, scenarioA)
    printSortResult(insertion, scenarioB)
    printSortResult(selection, scenarioA)
    printSortResult(selection, scenarioB)
    printSortResult(merge, scenarioA)
    printSortResult(merge, scenarioB)
    printSortResult(quick, scenarioA)
    printSortResult(quick, scenarioB)

    println("ScenarioA unchanged: ${scenarioA.values}")
    println("ScenarioB unchanged: ${scenarioB.values}")

    return DemoResult(DemoSection.SORTING.title, 12)
}

fun demoGraph(): DemoResult {
    printSection(DemoSection.GRAPH)

    val graph = Graph()
    graph.addEdge("A", "B")
    graph.addEdge("A", "C")
    graph.addEdge("B", "D")
    graph.addEdge("B", "E")
    graph.addEdge("C", "F")
    graph.addEdge("E", "G")
    graph.addEdge("F", "G")
    graph.addVertex("H")

    println("Graph structure:\n${graph}")
    println("Vertices sorted: ${graph.vertices().sorted()}")
    println("Vertex count: ${graph.vertexCount()}")
    println("Edge count: ${graph.getEdgeCount()}")
    println("Neighbors of B: ${graph.neighbors("B")}")
    println("Degree of G: ${graph.degree("G")}")
    println("Contains vertex H: ${graph.containsVertex("H")}")
    println("Contains edge A-C: ${graph.containsEdge("A", "C")}")
    println("BFS from A: ${graph.bfs("A")}")
    println("DFS from A: ${graph.dfs("A")}")
    println("Has path A-G: ${graph.hasPath("A", "G")}")
    println("Has path H-A: ${graph.hasPath("H", "A")}")
    println("Shortest path A-G: ${graph.shortestPath("A", "G")}")
    println("Shortest path D-F: ${graph.shortestPath("D", "F")}")
    println("Shortest path H-A: ${graph.shortestPath("H", "A")}")

    println("Remove edge F-G: ${graph.removeEdge("F", "G")}")
    println("Has path F-G after edge removal: ${graph.hasPath("F", "G")}")
    println("Remove vertex C: ${graph.removeVertex("C")}")
    println("Graph after removing C:\n${graph}")
    println("Vertices sorted after removal: ${graph.vertices().sorted()}")
    println("Edge count after removal: ${graph.getEdgeCount()}")

    return DemoResult(DemoSection.GRAPH.title, 18)
}

fun demoHashTable(): DemoResult {
    printSection(DemoSection.HASH_TABLE)

    val table = HashTable<Int>(5)
    println("Initially empty: ${table.isEmpty()}")

    table.put("ab", 10)
    table.put("ba", 20)
    table.put("cab", 30)
    table.put("dog", 40)
    table.put("god", 50)
    println("Table after inserts: $table")
    println("Size: ${table.size()}")
    println("Get ab: ${table.get("ab")}")
    println("Get ba: ${table.get("ba")}")
    println("Get missing: ${table.get("missing")}")
    println("Contains cab: ${table.containsKey("cab")}")
    println("Contains cat: ${table.containsKey("cat")}")
    println("Bucket 0: ${table.bucketView(0)}")
    println("Bucket 3: ${table.bucketView(3)}")
    println("Keys sorted: ${table.keys().sorted()}")
    println("Values sorted: ${table.values().sorted()}")
    println("Load factor: ${table.loadFactor()}")

    println("Update ba old value: ${table.put("ba", 22)}")
    println("Table after update: $table")
    println("Remove cab: ${table.remove("cab")}")
    println("Remove missing: ${table.remove("missing")}")
    println("Table after removals: $table")
    println("Entries snapshot size: ${table.entries().size}")

    table.clear()
    println("After clear size: ${table.size()}")
    println("After clear empty: ${table.isEmpty()}")

    return DemoResult(DemoSection.HASH_TABLE.title, 16)
}

fun demoPriorityQueue(): DemoResult {
    printSection(DemoSection.PRIORITY_QUEUE)

    val queue = PriorityQueue()
    println("Initially empty: ${queue.isEmpty()}")

    queue.enqueue(9)
    queue.enqueue(4)
    queue.enqueue(7)
    queue.enqueue(1)
    queue.enqueue(6)
    queue.enqueue(2)
    println("Queue after enqueues: $queue")
    println("Peek: ${queue.peek()}")
    println("Contains 7: ${queue.contains(7)}")
    println("Contains 99: ${queue.contains(99)}")
    println("Validate heap: ${queue.validateHeap()}")
    println("Array view: ${queue.toArrayList()}")

    println("Dequeue 1: ${queue.dequeue()}")
    println("Dequeue 2: ${queue.dequeue()}")
    println("Queue after dequeues: $queue")
    println("Peek after dequeues: ${queue.peek()}")
    println("Validate heap after dequeues: ${queue.validateHeap()}")

    val fromListValues = ArrayList<Int>()
    fromListValues.add(12)
    fromListValues.add(3)
    fromListValues.add(17)
    fromListValues.add(8)
    fromListValues.add(5)
    val built = PriorityQueue.fromList(fromListValues)
    println("Built from list: $built")
    println("Built queue peek: ${built.peek()}")
    println("Built queue validate: ${built.validateHeap()}")
    println("Built queue dequeue: ${built.dequeue()}")
    println("Built queue after dequeue: $built")

    queue.clear()
    println("After clear empty: ${queue.isEmpty()}")

    return DemoResult(DemoSection.PRIORITY_QUEUE.title, 14)
}

fun demoSummary(results: ArrayList<DemoResult>) {
    printSection(DemoSection.SUMMARY)

    var totalChecks = 0
    for (result in results) {
        println("${result.section}: ${result.checks} checks")
        totalChecks += result.checks
    }
    println("Total sections: ${results.size}")
    println("Total checks: $totalChecks")
}

fun main() {
    println("Kotlin DSA Project Demo")
    println("Deterministic data structures and algorithms output")

    val results = ArrayList<DemoResult>()
    results.add(demoLinkedList())
    results.add(demoStack())
    results.add(demoQueue())
    results.add(demoBinarySearchTree())
    results.add(demoSorting())
    results.add(demoGraph())
    results.add(demoHashTable())
    results.add(demoPriorityQueue())
    demoSummary(results)
}

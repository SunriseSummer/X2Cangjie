fun printSection(title: String) {
    println("=== $title ===")
}

fun printList(list: ArrayList<Long>): String {
    val builder = StringBuilder()
    builder.append("[")
    var i = 0
    while (i < list.size) {
        if (i > 0) builder.append(", ")
        builder.append(list[i].toString())
        i++
    }
    builder.append("]")
    return builder.toString()
}

fun main() {
    // Stack tests
    printSection("Stack")
    val stack = IntStack()
    stack.push(10L)
    stack.push(20L)
    stack.push(30L)
    println("Stack: $stack")
    println("Peek: ${stack.peek()}")
    println("Pop: ${stack.pop()}")
    println("Pop: ${stack.pop()}")
    println("Stack after pops: $stack")
    println("Size: ${stack.size()}")
    println("Empty: ${stack.isEmpty()}")
    stack.push(40L)
    stack.push(50L)
    println("After push 40, 50: $stack")

    // Queue tests
    printSection("Queue")
    val queue = IntQueue()
    queue.enqueue(1L)
    queue.enqueue(2L)
    queue.enqueue(3L)
    queue.enqueue(4L)
    println("Queue: $queue")
    println("Peek: ${queue.peek()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Queue after dequeues: $queue")
    println("Size: ${queue.size()}")
    queue.enqueue(5L)
    println("After enqueue 5: $queue")

    // MinHeap tests
    printSection("MinHeap")
    val heap = MinHeap()
    val heapValues = arrayListOf(42L, 15L, 8L, 23L, 4L, 16L, 31L)
    for (v in heapValues) {
        heap.insert(v)
    }
    println("Heap size: ${heap.size()}")
    println("Min: ${heap.peek()}")
    val extracted = ArrayList<Long>()
    while (!heap.isEmpty()) {
        extracted.add(heap.extractMin())
    }
    println("Extracted in order: ${printList(extracted)}")

    // BST tests
    printSection("BST")
    val bst = BST()
    val bstValues = arrayListOf(50L, 30L, 70L, 20L, 40L, 60L, 80L, 10L, 35L, 45L)
    for (v in bstValues) {
        bst.insert(v)
    }
    println("BST: $bst")
    println("Contains 40: ${bst.contains(40L)}")
    println("Contains 55: ${bst.contains(55L)}")
    println("Min: ${bst.min()}")
    println("Max: ${bst.max()}")
    println("Height: ${bst.height()}")
    println("Inorder: ${printList(bst.inorder())}")

    // Sorting tests
    printSection("Sorting")
    val sorter = Sorting()
    val unsorted = arrayListOf(64L, 34L, 25L, 12L, 22L, 11L, 90L, 1L)
    println("Original: ${printList(unsorted)}")
    println("Bubble sort: ${printList(sorter.bubbleSort(unsorted))}")
    println("Selection sort: ${printList(sorter.selectionSort(unsorted))}")
    println("Insertion sort: ${printList(sorter.insertionSort(unsorted))}")
    println("Merge sort: ${printList(sorter.mergeSort(unsorted))}")

    // Graph tests
    printSection("Graph")
    val graph = Graph()
    graph.addEdge("A", "B")
    graph.addEdge("A", "C")
    graph.addEdge("B", "D")
    graph.addEdge("C", "D")
    graph.addEdge("D", "E")
    graph.addEdge("B", "E")
    println("Graph:\n$graph")
    println("Vertices: ${graph.vertexCount()}")
    println("Neighbors of A: ${graph.neighbors("A")}")
    println("Neighbors of D: ${graph.neighbors("D")}")
    println("BFS from A: ${graph.bfs("A")}")
    println("DFS from A: ${graph.dfs("A")}")

    // HashTable tests
    printSection("HashTable")
    val table = HashTable()
    table.put("apple", 5L)
    table.put("banana", 3L)
    table.put("cherry", 8L)
    table.put("date", 2L)
    table.put("elderberry", 7L)
    println("Size: ${table.size()}")
    val apple1 = table.get("apple")
    val apple1Str = if (apple1 != null) apple1.toString() else "null"
    println("Get apple: $apple1Str")
    val banana1 = table.get("banana")
    val banana1Str = if (banana1 != null) banana1.toString() else "null"
    println("Get banana: $banana1Str")
    val fig1 = table.get("fig")
    val fig1Str = if (fig1 != null) fig1.toString() else "null"
    println("Get fig: $fig1Str")
    println("Contains cherry: ${table.hasKey("cherry")}")
    println("Contains fig: ${table.hasKey("fig")}")
    table.put("apple", 10L)
    val apple2 = table.get("apple")
    val apple2Str = if (apple2 != null) apple2.toString() else "null"
    println("Updated apple: $apple2Str")
    table.remove("date")
    println("After remove date, size: ${table.size()}")
    println("Contains date: ${table.hasKey("date")}")

    // Combined test: sort heap-extracted values
    printSection("Combined")
    val heap2 = MinHeap()
    val randomVals = arrayListOf(99L, 3L, 45L, 67L, 12L, 89L, 1L, 34L)
    for (v in randomVals) {
        heap2.insert(v)
    }
    val heapExtracted = ArrayList<Long>()
    while (!heap2.isEmpty()) {
        heapExtracted.add(heap2.extractMin())
    }
    println("Heap sort result: ${printList(heapExtracted)}")

    // Stack-based expression evaluation
    val evalStack = IntStack()
    // Evaluate: 3 4 + 2 * = (3+4)*2 = 14
    evalStack.push(3L)
    evalStack.push(4L)
    val a = evalStack.pop()
    val b = evalStack.pop()
    evalStack.push(a + b)
    evalStack.push(2L)
    val c = evalStack.pop()
    val d = evalStack.pop()
    evalStack.push(c * d)
    println("RPN (3 4 + 2 *) = ${evalStack.pop()}")

    // BFS shortest path via graph
    val pathGraph = Graph()
    pathGraph.addEdge("start", "mid1")
    pathGraph.addEdge("start", "mid2")
    pathGraph.addEdge("mid1", "end")
    pathGraph.addEdge("mid2", "mid3")
    pathGraph.addEdge("mid3", "end")
    println("BFS from start: ${pathGraph.bfs("start")}")
    println("DFS from start: ${pathGraph.dfs("start")}")
}

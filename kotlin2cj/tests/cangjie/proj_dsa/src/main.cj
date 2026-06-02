package proj_dsa

import std.collection.*

func printSection(title: String) {
    println("=== ${title} ===")
}

func printList(list: ArrayList<Int64>): String {
    let builder = StringBuilder()
    builder.append("[")
    var i = 0
    while (i < list.size) {
        if (i > 0) {
            builder.append(", ")
        }
        builder.append(list[i].toString())
        i += 1
    }
    builder.append("]")
    return builder.toString()
}

main() {
    printSection("Stack")
    let stack = IntStack()
    stack.push(10)
    stack.push(20)
    stack.push(30)
    println("Stack: ${stack}")
    println("Peek: ${stack.peek()}")
    println("Pop: ${stack.pop()}")
    println("Pop: ${stack.pop()}")
    println("Stack after pops: ${stack}")
    println("Size: ${stack.size()}")
    println("Empty: ${stack.isEmpty()}")
    stack.push(40)
    stack.push(50)
    println("After push 40, 50: ${stack}")
    printSection("Queue")
    let queue = IntQueue()
    queue.enqueue(1)
    queue.enqueue(2)
    queue.enqueue(3)
    queue.enqueue(4)
    println("Queue: ${queue}")
    println("Peek: ${queue.peek()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Queue after dequeues: ${queue}")
    println("Size: ${queue.size()}")
    queue.enqueue(5)
    println("After enqueue 5: ${queue}")
    printSection("MinHeap")
    let heap = MinHeap()
    let heapValues = ArrayList([42, 15, 8, 23, 4, 16, 31])
    for (v in heapValues) {
        heap.insert(v)
    }
    println("Heap size: ${heap.size()}")
    println("Min: ${heap.peek()}")
    let extracted = ArrayList<Int64>()
    while (!heap.isEmpty()) {
        extracted.add(heap.extractMin())
    }
    println("Extracted in order: ${printList(extracted)}")
    printSection("BST")
    let bst = BST()
    let bstValues = ArrayList([50, 30, 70, 20, 40, 60, 80, 10, 35, 45])
    for (v in bstValues) {
        bst.insert(v)
    }
    println("BST: ${bst}")
    println("Contains 40: ${bst.contains(40)}")
    println("Contains 55: ${bst.contains(55)}")
    println("Min: ${bst.min()}")
    println("Max: ${bst.max()}")
    println("Height: ${bst.height()}")
    println("Inorder: ${printList(bst.inorder())}")
    printSection("Sorting")
    let sorter = Sorting()
    let unsorted = ArrayList([64, 34, 25, 12, 22, 11, 90, 1])
    println("Original: ${printList(unsorted)}")
    println("Bubble sort: ${printList(sorter.bubbleSort(unsorted))}")
    println("Selection sort: ${printList(sorter.selectionSort(unsorted))}")
    println("Insertion sort: ${printList(sorter.insertionSort(unsorted))}")
    println("Merge sort: ${printList(sorter.mergeSort(unsorted))}")
    printSection("Graph")
    let graph = Graph()
    graph.addEdge("A", "B")
    graph.addEdge("A", "C")
    graph.addEdge("B", "D")
    graph.addEdge("C", "D")
    graph.addEdge("D", "E")
    graph.addEdge("B", "E")
    println("Graph:\n${graph}")
    println("Vertices: ${graph.vertexCount()}")
    println("Neighbors of A: ${graph.neighbors("A")}")
    println("Neighbors of D: ${graph.neighbors("D")}")
    println("BFS from A: ${graph.bfs("A")}")
    println("DFS from A: ${graph.dfs("A")}")
    printSection("HashTable")
    let table = HashTable()
    table.put("apple", 5)
    table.put("banana", 3)
    table.put("cherry", 8)
    table.put("date", 2)
    table.put("elderberry", 7)
    println("Size: ${table.size()}")
    let apple1 = table.get("apple")
    let apple1Str = if (let Some(apple1) <- apple1) {
        apple1.toString()
    } else {
        "null"
    }
    println("Get apple: ${apple1Str}")
    let banana1 = table.get("banana")
    let banana1Str = if (let Some(banana1) <- banana1) {
        banana1.toString()
    } else {
        "null"
    }
    println("Get banana: ${banana1Str}")
    let fig1 = table.get("fig")
    let fig1Str = if (let Some(fig1) <- fig1) {
        fig1.toString()
    } else {
        "null"
    }
    println("Get fig: ${fig1Str}")
    println("Contains cherry: ${table.hasKey("cherry")}")
    println("Contains fig: ${table.hasKey("fig")}")
    table.put("apple", 10)
    let apple2 = table.get("apple")
    let apple2Str = if (let Some(apple2) <- apple2) {
        apple2.toString()
    } else {
        "null"
    }
    println("Updated apple: ${apple2Str}")
    table.remove("date")
    println("After remove date, size: ${table.size()}")
    println("Contains date: ${table.hasKey("date")}")
    printSection("Combined")
    let heap2 = MinHeap()
    let randomVals = ArrayList([99, 3, 45, 67, 12, 89, 1, 34])
    for (v in randomVals) {
        heap2.insert(v)
    }
    let heapExtracted = ArrayList<Int64>()
    while (!heap2.isEmpty()) {
        heapExtracted.add(heap2.extractMin())
    }
    println("Heap sort result: ${printList(heapExtracted)}")
    let evalStack = IntStack()
    evalStack.push(3)
    evalStack.push(4)
    let a = evalStack.pop()
    let b = evalStack.pop()
    evalStack.push(a + b)
    evalStack.push(2)
    let c = evalStack.pop()
    let d = evalStack.pop()
    evalStack.push(c * d)
    println("RPN (3 4 + 2 *) = ${evalStack.pop()}")
    let pathGraph = Graph()
    pathGraph.addEdge("start", "mid1")
    pathGraph.addEdge("start", "mid2")
    pathGraph.addEdge("mid1", "end")
    pathGraph.addEdge("mid2", "mid3")
    pathGraph.addEdge("mid3", "end")
    println("BFS from start: ${pathGraph.bfs("start")}")
    println("DFS from start: ${pathGraph.dfs("start")}")
}

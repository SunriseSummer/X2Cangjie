package proj_dsa

import std.collection.*

class BST <: ToString {
    let values = ArrayList<Int64>()
    let leftChild = ArrayList<Int64>()
    let rightChild = ArrayList<Int64>()
    var rootIdx: Int64 = -1
    func insert(value: Int64): Unit {
        let newIdx = values.size
        values.add(value)
        leftChild.add(-1)
        rightChild.add(-1)
        if (rootIdx < 0) {
            rootIdx = newIdx
            return
        }
        var curr = rootIdx
        while (true) {
            if (value < values[curr]) {
                if (leftChild[curr] < 0) {
                    leftChild[curr] = newIdx
                    return
                }
                curr = leftChild[curr]
            } else if (value > values[curr]) {
                if (rightChild[curr] < 0) {
                    rightChild[curr] = newIdx
                    return
                }
                curr = rightChild[curr]
            } else {
                values.remove(at: values.size - 1)
                leftChild.remove(at: leftChild.size - 1)
                rightChild.remove(at: rightChild.size - 1)
                return
            }
        }
    }
    func contains(value: Int64): Bool {
        var curr = rootIdx
        while (curr >= 0) {
            if (value == values[curr]) {
                return true
            }
            curr = if (value < values[curr]) {
                leftChild[curr]
            } else {
                rightChild[curr]
            }
        }
        return false
    }
    func inorder(): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        inorderHelper(rootIdx, result)
        return result
    }
    func inorderHelper(idx: Int64, result: ArrayList<Int64>): Unit {
        if (idx < 0) {
            return
        }
        inorderHelper(leftChild[idx], result)
        result.add(values[idx])
        inorderHelper(rightChild[idx], result)
    }
    func min(): Int64 {
        var curr = rootIdx
        while (leftChild[curr] >= 0) {
            curr = leftChild[curr]
        }
        return values[curr]
    }
    func max(): Int64 {
        var curr = rootIdx
        while (rightChild[curr] >= 0) {
            curr = rightChild[curr]
        }
        return values[curr]
    }
    func size(): Int64 {
        return values.size
    }
    func height(): Int64 {
        return heightHelper(rootIdx)
    }
    func heightHelper(idx: Int64): Int64 {
        if (idx < 0) {
            return 0
        }
        let lh = heightHelper(leftChild[idx])
        let rh = heightHelper(rightChild[idx])
        return 1 + (if (lh > rh) { lh } else { rh })
    }
    public override func toString(): String {
        return "BST(size=${values.size}, inorder=${inorder()})"
    }
}

class Graph <: ToString {
    let labels = ArrayList<String>()
    let adjacency = ArrayList<ArrayList<Int64>>()
    let vertexIndex = HashMap<String, Int64>()
    func addVertex(label: String): Bool {
        if (vertexIndex.contains(label)) {
            return false
        }
        vertexIndex[label] = labels.size
        labels.add(label)
        adjacency.add(ArrayList<Int64>())
        return true
    }
    func getIdx(label: String): Int64 {
        if (!vertexIndex.contains(label)) {
            return -1
        }
        return vertexIndex[label]
    }
    func addEdge(from: String, to: String): Bool {
        addVertex(from)
        addVertex(to)
        let fi = getIdx(from)
        let ti = getIdx(to)
        if ((fi < 0) || (ti < 0)) {
            return false
        }
        if (hasEdge(fi, ti)) {
            return false
        }
        adjacency[fi].add(ti)
        adjacency[ti].add(fi)
        return true
    }
    func hasEdge(a: Int64, b: Int64): Bool {
        for (v in adjacency[a]) {
            if (v == b) {
                return true
            }
        }
        return false
    }
    func neighbors(label: String): ArrayList<String> {
        let result = ArrayList<String>()
        let idx = getIdx(label)
        if (idx < 0) {
            return result
        }
        for (ni in adjacency[idx]) {
            result.add(labels[ni])
        }
        return result
    }
    func bfs(start: String): ArrayList<String> {
        let order = ArrayList<String>()
        let si = getIdx(start)
        if (si < 0) {
            return order
        }
        let visited = HashSet<Int64>()
        let queue = ArrayList<Int64>()
        var head = 0
        visited.add(si)
        queue.add(si)
        while (head < queue.size) {
            let curr = queue[head]
            head += 1
            order.add(labels[curr])
            for (ni in adjacency[curr]) {
                if (!visited.contains(ni)) {
                    visited.add(ni)
                    queue.add(ni)
                }
            }
        }
        return order
    }
    func dfs(start: String): ArrayList<String> {
        let order = ArrayList<String>()
        let si = getIdx(start)
        if (si < 0) {
            return order
        }
        let visited = HashSet<Int64>()
        dfsHelper(si, visited, order)
        return order
    }
    func dfsHelper(idx: Int64, visited: HashSet<Int64>, order: ArrayList<String>): Unit {
        visited.add(idx)
        order.add(labels[idx])
        for (ni in adjacency[idx]) {
            if (!visited.contains(ni)) {
                dfsHelper(ni, visited, order)
            }
        }
    }
    func vertexCount(): Int64 {
        return labels.size
    }
    public override func toString(): String {
        let builder = StringBuilder()
        var i = 0
        while (i < labels.size) {
            builder.append(labels[i])
            builder.append(" -> ")
            builder.append(neighbors(labels[i]).toString())
            if (i < (labels.size - 1)) {
                builder.append("\n")
            }
            i += 1
        }
        return builder.toString()
    }
}

class HashTable <: ToString {
    init() {
        var i = 0
        while (i < capacity) {
            keys.add(ArrayList<String>())
            vals.add(ArrayList<Int64>())
            i += 1
        }
    }
    let capacity: Int64 = 16
    let keys = ArrayList<ArrayList<String>>()
    let vals = ArrayList<ArrayList<Int64>>()
    var count: Int64 = 0
    func hash(key: String): Int64 {
        var h = 0
        var i = 0
        while (i < key.size) {
            h = (h * 31) + Int64(UInt32(key.toRuneArray()[i]))
            i += 1
        }
        if (h < 0) {
            h = -h
        }
        return h % capacity
    }
    func put(key: String, value: Int64) {
        let idx = hash(key)
        let bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                vals[idx][i] = value
                return
            }
            i += 1
        }
        bucket.add(key)
        vals[idx].add(value)
        count += 1
    }
    func get(key: String): ?Int64 {
        let idx = hash(key)
        let bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                return vals[idx][i]
            }
            i += 1
        }
        return None
    }
    func hasKey(key: String): Bool {
        return get(key).isSome()
    }
    func remove(key: String): Bool {
        let idx = hash(key)
        let bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                bucket.remove(at: i)
                vals[idx].remove(at: i)
                count -= 1
                return true
            }
            i += 1
        }
        return false
    }
    func size(): Int64 {
        return count
    }
    func allKeys(): ArrayList<String> {
        let result = ArrayList<String>()
        var i = 0
        while (i < capacity) {
            for (key in keys[i]) {
                result.add(key)
            }
            i += 1
        }
        return result
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("HashTable{")
        var first = true
        var i = 0
        while (i < capacity) {
            var j = 0
            while (j < keys[i].size) {
                if (!first) {
                    builder.append(", ")
                }
                builder.append(keys[i][j])
                builder.append("=")
                builder.append(vals[i][j].toString())
                first = false
                j += 1
            }
            i += 1
        }
        builder.append("}")
        return builder.toString()
    }
}

class MinHeap <: ToString {
    let data = ArrayList<Int64>()
    func insert(value: Int64) {
        data.add(value)
        siftUp(data.size - 1)
    }
    func extractMin(): Int64 {
        let min = data[0]
        let last = data[data.size - 1]
        data.remove(at: data.size - 1)
        if (data.size > 0) {
            data[0] = last
            siftDown(0)
        }
        return min
    }
    func peek(): Int64 {
        return data[0]
    }
    func isEmpty(): Bool {
        return data.size == 0
    }
    func size(): Int64 {
        return data.size
    }
    func siftUp(index: Int64) {
        var i = index
        while (i > 0) {
            let parent = (i - 1) / 2
            if (data[i] < data[parent]) {
                let temp = data[i]
                data[i] = data[parent]
                data[parent] = temp
                i = parent
            } else {
                break
            }
        }
    }
    func siftDown(index: Int64) {
        var i = index
        while (true) {
            var smallest = i
            let left = (2 * i) + 1
            let right = (2 * i) + 2
            if ((left < data.size) && (data[left] < data[smallest])) {
                smallest = left
            }
            if ((right < data.size) && (data[right] < data[smallest])) {
                smallest = right
            }
            if (smallest != i) {
                let temp = data[i]
                data[i] = data[smallest]
                data[smallest] = temp
                i = smallest
            } else {
                break
            }
        }
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Heap[")
        var i = 0
        while (i < data.size) {
            if (i > 0) {
                builder.append(", ")
            }
            builder.append(data[i].toString())
            i += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

class IntQueue <: ToString {
    let items = ArrayList<Int64>()
    var head: Int64 = 0
    func enqueue(value: Int64) {
        items.add(value)
    }
    func dequeue(): Int64 {
        let value = items[head]
        head += 1
        return value
    }
    func peek(): Int64 {
        return items[head]
    }
    func isEmpty(): Bool {
        return head >= items.size
    }
    func size(): Int64 {
        return items.size - head
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Queue[")
        var i = head
        var first = true
        while (i < items.size) {
            if (!first) {
                builder.append(", ")
            }
            builder.append(items[i].toString())
            first = false
            i += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

class Sorting {
    func bubbleSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (v in arr) {
            result.add(v)
        }
        var n = result.size
        var i = 0
        while (i < (n - 1)) {
            var j = 0
            while (j < ((n - 1) - i)) {
                if (result[j] > result[j + 1]) {
                    let temp = result[j]
                    result[j] = result[j + 1]
                    result[j + 1] = temp
                }
                j += 1
            }
            i += 1
        }
        return result
    }
    func selectionSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (v in arr) {
            result.add(v)
        }
        var n = result.size
        var i = 0
        while (i < (n - 1)) {
            var minIdx = i
            var j = i + 1
            while (j < n) {
                if (result[j] < result[minIdx]) {
                    minIdx = j
                }
                j += 1
            }
            if (minIdx != i) {
                let temp = result[i]
                result[i] = result[minIdx]
                result[minIdx] = temp
            }
            i += 1
        }
        return result
    }
    func insertionSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (v in arr) {
            result.add(v)
        }
        var i = 1
        while (i < result.size) {
            let key = result[i]
            var j = i - 1
            while ((j >= 0) && (result[j] > key)) {
                result[j + 1] = result[j]
                j -= 1
            }
            result[j + 1] = key
            i += 1
        }
        return result
    }
    func mergeSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        if (arr.size <= 1) {
            return arr
        }
        let mid = arr.size / 2
        let leftArr = ArrayList<Int64>()
        let rightArr = ArrayList<Int64>()
        var i = 0
        while (i < mid) {
            leftArr.add(arr[i])
            i += 1
        }
        while (i < arr.size) {
            rightArr.add(arr[i])
            i += 1
        }
        let sortedLeft = mergeSort(leftArr)
        let sortedRight = mergeSort(rightArr)
        return merge(sortedLeft, sortedRight)
    }
    func merge(left: ArrayList<Int64>, right: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        var i = 0
        var j = 0
        while ((i < left.size) && (j < right.size)) {
            if (left[i] <= right[j]) {
                result.add(left[i])
                i += 1
            } else {
                result.add(right[j])
                j += 1
            }
        }
        while (i < left.size) {
            result.add(left[i])
            i += 1
        }
        while (j < right.size) {
            result.add(right[j])
            j += 1
        }
        return result
    }
}

class IntStack <: ToString {
    let items = ArrayList<Int64>()
    func push(value: Int64) {
        items.add(value)
    }
    func pop(): Int64 {
        let last = items[items.size - 1]
        items.remove(at: items.size - 1)
        return last
    }
    func peek(): Int64 {
        return items[items.size - 1]
    }
    func isEmpty(): Bool {
        return items.size == 0
    }
    func size(): Int64 {
        return items.size
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Stack[")
        var i = 0
        while (i < items.size) {
            if (i > 0) {
                builder.append(", ")
            }
            builder.append(items[i].toString())
            i += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

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
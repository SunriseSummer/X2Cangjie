package proj_dsa

import std.collection.*
import std.convert.*
import std.deriving.*
import std.sort.*

class TreeNode {
    var value: Int64
    var left: ?TreeNode
    var right: ?TreeNode
    init(value: Int64, left!: ?TreeNode = None, right!: ?TreeNode = None) {
        this.value = value
        this.left = left
        this.right = right
    }
}

class BinarySearchTree <: ToString {
    var root: ?TreeNode = None
    var count: Int64 = 0
    func insert(value: Int64): Bool {
        let inserted = insertNode(root, value)
        root = inserted[0]
        if (inserted[1]) {
            count += 1
        }
        return inserted[1]
    }
    func insertAll(values: ArrayList<Int64>) {
        for (value in values) {
            insert(value)
        }
    }
    func insertNode(node: ?TreeNode, value: Int64): (?TreeNode, Bool) {
        if (node.isNone()) {
            return (TreeNode(value), true)
        }
        return if (value < node.getOrThrow().value) {
            let inserted = insertNode(node.getOrThrow().left, value)
            node.getOrThrow().left = inserted[0]
            (node, inserted[1])
        } else if (value > node.getOrThrow().value) {
            let inserted = insertNode(node.getOrThrow().right, value)
            node.getOrThrow().right = inserted[0]
            (node, inserted[1])
        } else {
            (node, false)
        }
    }
    func search(value: Int64): ?TreeNode {
        var current = root
        while (current.isSome()) {
            current = if (value < current.getOrThrow().value) {
                current.getOrThrow().left
            } else if (value > current.getOrThrow().value) {
                current.getOrThrow().right
            } else {
                return current
            }
        }
        return None
    }
    func contains(value: Int64): Bool {
        return search(value).isSome()
    }
    func delete(value: Int64): Bool {
        let deleted = deleteNode(root, value)
        root = deleted[0]
        if (deleted[1]) {
            count -= 1
        }
        return deleted[1]
    }
    func deleteNode(node: ?TreeNode, value: Int64): (?TreeNode, Bool) {
        if (node.isNone()) {
            return (None, false)
        }
        return if (value < node.getOrThrow().value) {
            let deleted = deleteNode(node.getOrThrow().left, value)
            node.getOrThrow().left = deleted[0]
            (node, deleted[1])
        } else if (value > node.getOrThrow().value) {
            let deleted = deleteNode(node.getOrThrow().right, value)
            node.getOrThrow().right = deleted[0]
            (node, deleted[1])
        } else {
            if ((node.getOrThrow().left.isNone()) && (node.getOrThrow().right.isNone())) {
                (None, true)
            } else if (node.getOrThrow().left.isNone()) {
                (node.getOrThrow().right, true)
            } else if (node.getOrThrow().right.isNone()) {
                (node.getOrThrow().left, true)
            } else {
                let successor = findMinNode(node.getOrThrow().right).getOrThrow()
                node.getOrThrow().value = successor.value
                let deleted = deleteNode(node.getOrThrow().right, successor.value)
                node.getOrThrow().right = deleted[0]
                (node, true)
            }
        }
    }
    func min(): ?Int64 {
        let node = findMinNode(root)
        if (let Some(node) <- node) {
            return node.value
        }
        return None
    }
    func max(): ?Int64 {
        var current = root
        while ((current.isSome()) && (current.getOrThrow().right.isSome())) {
            current = current.getOrThrow().right
        }
        if (let Some(current) <- current) {
            return current.value
        }
        return None
    }
    func findMinNode(node: ?TreeNode): ?TreeNode {
        var current = node
        while ((current.isSome()) && (current.getOrThrow().left.isSome())) {
            current = current.getOrThrow().left
        }
        return current
    }
    func height(): Int64 {
        return heightOf(root)
    }
    func heightOf(node: ?TreeNode): Int64 {
        if (node.isNone()) {
            return -1
        }
        let leftHeight = heightOf(node.getOrThrow().left)
        let rightHeight = heightOf(node.getOrThrow().right)
        return (if (leftHeight > rightHeight) { leftHeight } else { rightHeight }) + 1
    }
    func inorder(): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        fillInorder(root, result)
        return result
    }
    func fillInorder(node: ?TreeNode, result: ArrayList<Int64>): Unit {
        if (node.isNone()) {
            return
        }
        fillInorder(node.getOrThrow().left, result)
        result.add(node.getOrThrow().value)
        fillInorder(node.getOrThrow().right, result)
    }
    func preorder(): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        fillPreorder(root, result)
        return result
    }
    func fillPreorder(node: ?TreeNode, result: ArrayList<Int64>): Unit {
        if (node.isNone()) {
            return
        }
        result.add(node.getOrThrow().value)
        fillPreorder(node.getOrThrow().left, result)
        fillPreorder(node.getOrThrow().right, result)
    }
    func postorder(): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        fillPostorder(root, result)
        return result
    }
    func fillPostorder(node: ?TreeNode, result: ArrayList<Int64>): Unit {
        if (node.isNone()) {
            return
        }
        fillPostorder(node.getOrThrow().left, result)
        fillPostorder(node.getOrThrow().right, result)
        result.add(node.getOrThrow().value)
    }
    func levelOrder(): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        if (root.isNone()) {
            return result
        }
        let queue = Queue<TreeNode>()
        queue.enqueue(root.getOrThrow())
        while (!queue.isEmpty()) {
            let node = queue.dequeue().getOrThrow()
            result.add(node.value)
            if (node.left.isSome()) {
                queue.enqueue(node.left.getOrThrow())
            }
            if (node.right.isSome()) {
                queue.enqueue(node.right.getOrThrow())
            }
        }
        return result
    }
    func countLeaves(): Int64 {
        return countLeavesOf(root)
    }
    func countLeavesOf(node: ?TreeNode): Int64 {
        if (node.isNone()) {
            return 0
        }
        if ((node.getOrThrow().left.isNone()) && (node.getOrThrow().right.isNone())) {
            return 1
        }
        return countLeavesOf(node.getOrThrow().left) + countLeavesOf(node.getOrThrow().right)
    }
    func sum(): Int64 {
        return sumOf(root)
    }
    func sumOf(node: ?TreeNode): Int64 {
        if (node.isNone()) {
            return 0
        }
        return (node.getOrThrow().value + sumOf(node.getOrThrow().left)) + sumOf(node.getOrThrow().right)
    }
    func size(): Int64 {
        return count
    }
    func isEmpty(): Bool {
        return count == 0
    }
    func clear() {
        root = None
        count = 0
    }
    public override func toString(): String {
        return "BinarySearchTree${inorder()}"
    }
}

class Graph <: ToString {
    let adjacency = HashMap<String, ArrayList<String>>()
    var edgeCount: Int64 = 0
    func addVertex(vertex: String): Bool {
        if (adjacency.contains(vertex)) {
            return false
        }
        adjacency[vertex] = ArrayList<String>()
        return true
    }
    func addEdge(first: String, second: String): Bool {
        addVertex(first)
        addVertex(second)
        let firstNeighbors = adjacency[first]
        let secondNeighbors = adjacency[second]
        if (firstNeighbors.contains(second)) {
            return false
        }
        firstNeighbors.add(second)
        secondNeighbors.add(first)
        edgeCount += 1
        return true
    }
    func removeEdge(first: String, second: String): Bool {
        if (!adjacency.contains(first) || !adjacency.contains(second)) {
            return false
        }
        let firstList = adjacency[first]
        let secondList = adjacency[second]
        let idx1 = firstList.indexOf(second)
        let idx2 = secondList.indexOf(first)
        if ((idx1 >= 0) && (idx2 >= 0)) {
            firstList.remove(at: idx1)
            secondList.remove(at: idx2)
            edgeCount -= 1
            return true
        }
        return false
    }
    func removeVertex(vertex: String): Bool {
        let neighbors = adjacency.get(vertex) ?? return
        false
        let copy = ArrayList<String>()
        for (neighbor in neighbors) {
            copy.add(neighbor)
        }
        for (neighbor in copy) {
            removeEdge(vertex, neighbor)
        }
        adjacency.remove(vertex)
        return true
    }
    func containsVertex(vertex: String): Bool {
        return adjacency.contains(vertex)
    }
    func containsEdge(first: String, second: String): Bool {
        return adjacency.get(first)?.contains(second) ?? false
    }
    func neighbors(vertex: String): ArrayList<String> {
        let result = ArrayList<String>()
        let source = adjacency.get(vertex) ?? return
        result
        for (neighbor in source) {
            result.add(neighbor)
        }
        return result
    }
    func vertexCount(): Int64 {
        return adjacency.size
    }
    func getEdgeCount(): Int64 {
        return edgeCount
    }
    func degree(vertex: String): Int64 {
        return adjacency.get(vertex)?.size ?? 0
    }
    func vertices(): ArrayList<String> {
        let result = ArrayList<String>()
        for (key in adjacency.keys()) {
            result.add(key)
        }
        return result
    }
    func bfs(start: String): ArrayList<String> {
        let order = ArrayList<String>()
        if (!adjacency.contains(start)) {
            return order
        }
        let visited = HashSet<String>()
        let queue = Queue<String>()
        visited.add(start)
        queue.enqueue(start)
        while (!queue.isEmpty()) {
            let vertex = queue.dequeue().getOrThrow()
            order.add(vertex)
            let neighbors = adjacency[vertex]
            for (neighbor in neighbors) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor)
                    queue.enqueue(neighbor)
                }
            }
        }
        return order
    }
    func dfs(start: String): ArrayList<String> {
        let order = ArrayList<String>()
        if (!adjacency.contains(start)) {
            return order
        }
        let visited = HashSet<String>()
        dfsVisit(start, visited, order)
        return order
    }
    func dfsVisit(vertex: String, visited: HashSet<String>, order: ArrayList<String>): Unit {
        visited.add(vertex)
        order.add(vertex)
        let neighbors = adjacency[vertex]
        for (neighbor in neighbors) {
            if (!visited.contains(neighbor)) {
                dfsVisit(neighbor, visited, order)
            }
        }
    }
    func hasPath(start: String, end: String): Bool {
        if (!adjacency.contains(start) || !adjacency.contains(end)) {
            return false
        }
        let visited = HashSet<String>()
        return hasPathVisit(start, end, visited)
    }
    func hasPathVisit(current: String, end: String, visited: HashSet<String>): Bool {
        if (current == end) {
            return true
        }
        visited.add(current)
        let neighbors = adjacency[current]
        for (neighbor in neighbors) {
            if (!visited.contains(neighbor) && hasPathVisit(neighbor, end, visited)) {
                return true
            }
        }
        return false
    }
    func shortestPath(start: String, end: String): ArrayList<String> {
        let path = ArrayList<String>()
        if (!adjacency.contains(start) || !adjacency.contains(end)) {
            return path
        }
        let queue = Queue<String>()
        let visited = HashSet<String>()
        let parent = HashMap<String, String>()
        queue.enqueue(start)
        visited.add(start)
        parent[start] = ""
        while (!queue.isEmpty()) {
            let current = queue.dequeue().getOrThrow()
            if (current == end) {
                break
            }
            let neighbors = adjacency[current]
            for (neighbor in neighbors) {
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.enqueue(neighbor)
                }
            }
        }
        if (!visited.contains(end)) {
            return path
        }
        let reversed = ArrayList<String>()
        var current = end
        while (current != "") {
            reversed.add(current)
            current = parent.get(current) ?? ""
        }
        var index = reversed.size - 1
        while (index >= 0) {
            path.add(reversed[index])
            index -= 1
        }
        return path
    }
    public override func toString(): String {
        let builder = StringBuilder()
        let orderedVertices = ({ => let _s = collectArrayList(vertices().iterator()); sort(_s, stable: true); _s })()
        var index = 0
        while (index < orderedVertices.size) {
            let vertex = orderedVertices[index]
            builder.append(vertex)
            builder.append(" -> ")
            builder.append(adjacency[vertex])
            if (index < (orderedVertices.size - 1)) {
                builder.append("\n")
            }
            index += 1
        }
        return builder.toString()
    }
}

class HashEntry<V> <: ToString {
    let key: String
    var value: V
    init(key: String, value: V) {
        this.key = key
        this.value = value
    }
    public func toString(): String {
        return "HashEntry(key=${this.key}, value=${this.value})"
    }
}

class HashTable<V> <: ToString {
    let capacity: Int64
    init(capacity!: Int64 = 7) {
        this.capacity = capacity
        var index = 0
        while (index < capacity) {
            buckets.add(ArrayList<HashEntry<V>>())
            index += 1
        }
    }
    let buckets = ArrayList<ArrayList<HashEntry<V>>>()
    var count: Int64 = 0
    func hash(key: String): Int64 {
        var total = 0
        for (ch in key.runes()) {
            total += Int64(UInt32(ch))
        }
        return total % capacity
    }
    func put(key: String, value: V): ?V {
        let bucket = buckets[hash(key)]
        for (entry in bucket) {
            if (entry.key == key) {
                let oldValue = entry.value
                entry.value = value
                return oldValue
            }
        }
        bucket.add(HashEntry(key, value))
        count += 1
        return None
    }
    func get(key: String): ?V {
        let bucket = buckets[hash(key)]
        for (entry in bucket) {
            if (entry.key == key) {
                return entry.value
            }
        }
        return None
    }
    func remove(key: String): ?V {
        let bucket = buckets[hash(key)]
        var index = 0
        while (index < bucket.size) {
            if (bucket[index].key == key) {
                let value = bucket[index].value
                bucket.remove(at: index)
                count -= 1
                return value
            }
            index += 1
        }
        return None
    }
    func containsKey(key: String): Bool {
        return get(key).isSome()
    }
    func keys(): ArrayList<String> {
        let result = ArrayList<String>()
        for (bucket in buckets) {
            for (entry in bucket) {
                result.add(entry.key)
            }
        }
        return result
    }
    func values(): ArrayList<V> {
        let result = ArrayList<V>()
        for (bucket in buckets) {
            for (entry in bucket) {
                result.add(entry.value)
            }
        }
        return result
    }
    func entries(): ArrayList<HashEntry<V>> {
        let result = ArrayList<HashEntry<V>>()
        for (bucket in buckets) {
            for (entry in bucket) {
                result.add(HashEntry(entry.key, entry.value))
            }
        }
        return result
    }
    func size(): Int64 {
        return count
    }
    func isEmpty(): Bool {
        return count == 0
    }
    func loadFactor(): Float64 {
        if (capacity == 0) {
            return 0.0
        }
        return Float64(count) / Float64.parse(capacity)
    }
    func bucketView(index: Int64): String {
        if ((index < 0) || (index >= buckets.size)) {
            return "[]"
        }
        let builder = StringBuilder()
        builder.append("[")
        var entryIndex = 0
        while (entryIndex < buckets[index].size) {
            if (entryIndex > 0) {
                builder.append(", ")
            }
            let entry = buckets[index][entryIndex]
            builder.append(entry.key)
            builder.append("=")
            builder.append(entry.value)
            entryIndex += 1
        }
        builder.append("]")
        return builder.toString()
    }
    func clear() {
        for (bucket in buckets) {
            bucket.clear()
        }
        count = 0
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("HashTable{")
        var index = 0
        while (index < buckets.size) {
            if (index > 0) {
                builder.append(", ")
            }
            builder.append(index)
            builder.append(":")
            builder.append(bucketView(index))
            index += 1
        }
        builder.append("}")
        return builder.toString()
    }
}

class LinkedListNode<T> {
    var value: T
    var next: ?LinkedListNode<T>
    init(value: T, next!: ?LinkedListNode<T> = None) {
        this.value = value
        this.next = next
    }
}

class LinkedList<T> <: ToString {
    var head: ?LinkedListNode<T> = None
    var tail: ?LinkedListNode<T> = None
    var count: Int64 = 0
    func addFirst(value: T) {
        let node = LinkedListNode(value, next: head)
        head = node
        if (tail.isNone()) {
            tail = node
        }
        count += 1
    }
    func addLast(value: T) {
        let node = LinkedListNode(value, next: None)
        if (head.isNone()) {
            head = node
            tail = node
        } else {
            tail.getOrThrow().next = node
            tail = node
        }
        count += 1
    }
    func addAt(index: Int64, value: T): Bool {
        if ((index < 0) || (index > count)) {
            return false
        }
        if (index == 0) {
            addFirst(value)
            return true
        }
        if (index == count) {
            addLast(value)
            return true
        }
        var currentIndex = 0
        var previous = head
        while ((previous.isSome()) && (currentIndex < (index - 1))) {
            previous = previous.getOrThrow().next
            currentIndex += 1
        }
        if (previous.isNone()) {
            return false
        }
        let node = LinkedListNode(value, next: previous.getOrThrow().next)
        previous.getOrThrow().next = node
        count += 1
        return true
    }
    func removeFirst(): ?T {
        if (head.isNone()) {
            return None
        }
        let value = head.getOrThrow().value
        head = head.getOrThrow().next
        if (head.isNone()) {
            tail = None
        }
        count -= 1
        return value
    }
    func removeLast(): ?T {
        if (head.isNone()) {
            return None
        }
        if (head == tail) {
            let value = head.getOrThrow().value
            head = None
            tail = None
            count = 0
            return value
        }
        var previous = head
        while ((previous.isSome()) && (previous.getOrThrow().next != tail)) {
            previous = previous.getOrThrow().next
        }
        let value = tail.getOrThrow().value
        tail = previous
        tail.getOrThrow().next = None
        count -= 1
        return value
    }
    func remove(value: T): Bool {
        if (head.isNone()) {
            return false
        }
        if (head.getOrThrow().value == value) {
            removeFirst()
            return true
        }
        var previous = head
        while ((previous.isSome()) && (previous.getOrThrow().next.isSome())) {
            if (previous.getOrThrow().next.getOrThrow().value == value) {
                if (previous.getOrThrow().next == tail) {
                    tail = previous
                }
                previous.getOrThrow().next = previous.getOrThrow().next.getOrThrow().next
                count -= 1
                return true
            }
            previous = previous.getOrThrow().next
        }
        return false
    }
    func removeAt(index: Int64): ?T {
        if ((index < 0) || (index >= count)) {
            return None
        }
        if (index == 0) {
            return removeFirst()
        }
        var currentIndex = 0
        var previous = head
        while ((previous.isSome()) && (currentIndex < (index - 1))) {
            previous = previous.getOrThrow().next
            currentIndex += 1
        }
        if ((previous.isNone()) || (previous.getOrThrow().next.isNone())) {
            return None
        }
        let removed = previous.getOrThrow().next.getOrThrow()
        previous.getOrThrow().next = removed.next
        if (removed == tail) {
            tail = previous
        }
        count -= 1
        return removed.value
    }
    func find(value: T): ?LinkedListNode<T> {
        var current = head
        while (current.isSome()) {
            if (current.getOrThrow().value == value) {
                return current
            }
            current = current.getOrThrow().next
        }
        return None
    }
    func contains(value: T): Bool {
        return find(value).isSome()
    }
    func indexOf(value: T): Int64 {
        var index = 0
        var current = head
        while (current.isSome()) {
            if (current.getOrThrow().value == value) {
                return index
            }
            current = current.getOrThrow().next
            index += 1
        }
        return -1
    }
    func get(index: Int64): ?T {
        if ((index < 0) || (index >= count)) {
            return None
        }
        var currentIndex = 0
        var current = head
        while (current.isSome()) {
            if (currentIndex == index) {
                return current.getOrThrow().value
            }
            current = current.getOrThrow().next
            currentIndex += 1
        }
        return None
    }
    func set(index: Int64, value: T): Bool {
        if ((index < 0) || (index >= count)) {
            return false
        }
        var currentIndex = 0
        var current = head
        while (current.isSome()) {
            if (currentIndex == index) {
                current.getOrThrow().value = value
                return true
            }
            current = current.getOrThrow().next
            currentIndex += 1
        }
        return false
    }
    func reverse() {
        var previous: ?LinkedListNode<T> = None
        var current = head
        tail = head
        while (current.isSome()) {
            let nextNode = current.getOrThrow().next
            current.getOrThrow().next = previous
            previous = current
            current = nextNode
        }
        head = previous
    }
    func clear() {
        head = None
        tail = None
        count = 0
    }
    func size(): Int64 {
        return count
    }
    func isEmpty(): Bool {
        return count == 0
    }
    func toArrayList(): ArrayList<T> {
        let result = ArrayList<T>()
        var current = head
        while (current.isSome()) {
            result.add(current.getOrThrow().value)
            current = current.getOrThrow().next
        }
        return result
    }
    func copy(): LinkedList<T> {
        let copied = LinkedList<T>()
        var current = head
        while (current.isSome()) {
            copied.addLast(current.getOrThrow().value)
            current = current.getOrThrow().next
        }
        return copied
    }
    func join(separator!: String = " -> "): String {
        let builder = StringBuilder()
        var current = head
        var first = true
        while (current.isSome()) {
            if (!first) {
                builder.append(separator)
            }
            builder.append(current.getOrThrow().value)
            first = false
            current = current.getOrThrow().next
        }
        return builder.toString()
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("LinkedList[")
        var current = head
        var first = true
        while (current.isSome()) {
            if (!first) {
                builder.append(", ")
            }
            builder.append(current.getOrThrow().value)
            first = false
            current = current.getOrThrow().next
        }
        builder.append("]")
        return builder.toString()
    }
}

class PriorityQueue <: ToString {
    let heap = ArrayList<Int64>()
    static func fromList(values: ArrayList<Int64>): PriorityQueue {
        let queue = PriorityQueue()
        queue.buildFrom(values)
        return queue
    }
    func enqueue(value: Int64) {
        heap.add(value)
        bubbleUp(heap.size - 1)
    }
    func dequeue(): ?Int64 {
        if (heap.isEmpty()) {
            return None
        }
        if (heap.size == 1) {
            return heap.remove(at: 0)
        }
        let value = heap[0]
        let last = heap.remove(at: heap.size - 1)
        heap[0] = last
        bubbleDown(0)
        return value
    }
    func peek(): ?Int64 {
        if (heap.isEmpty()) {
            return None
        }
        return heap[0]
    }
    func isEmpty(): Bool {
        return heap.isEmpty()
    }
    func size(): Int64 {
        return heap.size
    }
    func clear() {
        heap.clear()
    }
    func contains(value: Int64): Bool {
        return heap.contains(value)
    }
    func buildFrom(values: ArrayList<Int64>) {
        clear()
        for (value in values) {
            heap.add(value)
        }
        var index = parentIndex(heap.size - 1)
        while (index >= 0) {
            bubbleDown(index)
            index -= 1
        }
    }
    func parentIndex(index: Int64): Int64 {
        return (index - 1) / 2
    }
    func leftChildIndex(index: Int64): Int64 {
        return (index * 2) + 1
    }
    func rightChildIndex(index: Int64): Int64 {
        return (index * 2) + 2
    }
    func bubbleUp(startIndex: Int64) {
        var index = startIndex
        while (index > 0) {
            let parent = parentIndex(index)
            if (heap[parent] <= heap[index]) {
                break
            }
            swap(parent, index)
            index = parent
        }
    }
    func bubbleDown(startIndex: Int64) {
        var index = startIndex
        while (true) {
            let left = leftChildIndex(index)
            let right = rightChildIndex(index)
            var smallest = index
            if ((left < heap.size) && (heap[left] < heap[smallest])) {
                smallest = left
            }
            if ((right < heap.size) && (heap[right] < heap[smallest])) {
                smallest = right
            }
            if (smallest == index) {
                break
            }
            swap(index, smallest)
            index = smallest
        }
    }
    func swap(first: Int64, second: Int64) {
        let temp = heap[first]
        heap[first] = heap[second]
        heap[second] = temp
    }
    func validateHeap(): Bool {
        var index = 0
        while (index < heap.size) {
            let left = leftChildIndex(index)
            let right = rightChildIndex(index)
            if ((left < heap.size) && (heap[index] > heap[left])) {
                return false
            }
            if ((right < heap.size) && (heap[index] > heap[right])) {
                return false
            }
            index += 1
        }
        return true
    }
    func toArrayList(): ArrayList<Int64> {
        let copied = ArrayList<Int64>()
        for (value in heap) {
            copied.add(value)
        }
        return copied
    }
    public override func toString(): String {
        return "PriorityQueue${heap}"
    }
}

class Queue<T> <: ToString {
    let items = ArrayList<T>()
    func enqueue(value: T) {
        items.add(value)
    }
    func enqueueAll(values: ArrayList<T>) {
        for (value in values) {
            enqueue(value)
        }
    }
    func dequeue(): ?T {
        if (items.isEmpty()) {
            return None
        }
        let value = items[0]
        items.remove(at: 0)
        return value
    }
    func peek(): ?T {
        if (items.isEmpty()) {
            return None
        }
        return items[0]
    }
    func isEmpty(): Bool {
        return items.isEmpty()
    }
    func size(): Int64 {
        return items.size
    }
    func clear() {
        items.clear()
    }
    func contains(value: T): Bool {
        return items.contains(value)
    }
    func rotate() {
        if (items.size <= 1) {
            return
        }
        let front = dequeue()
        if (let Some(front) <- front) {
            enqueue(front)
        }
    }
    func toArrayList(): ArrayList<T> {
        let copied = ArrayList<T>()
        for (item in items) {
            copied.add(item)
        }
        return copied
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Queue[")
        var index = 0
        while (index < items.size) {
            if (index > 0) {
                builder.append(", ")
            }
            builder.append(items[index])
            index += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

interface Sorter {
    func name(): String
    func sort(list: ArrayList<Int64>): ArrayList<Int64>
}

abstract class BaseSorter <: Sorter & ToString {
    public open func copyInput(list: ArrayList<Int64>): ArrayList<Int64> {
        let copied = ArrayList<Int64>()
        for (value in list) {
            copied.add(value)
        }
        return copied
    }
    public open func swap(list: ArrayList<Int64>, first: Int64, second: Int64) {
        let temp = list[first]
        list[first] = list[second]
        list[second] = temp
    }
    public open func isSorted(list: ArrayList<Int64>): Bool {
        if (list.size <= 1) {
            return true
        }
        var index = 1
        while (index < list.size) {
            if (list[index - 1] > list[index]) {
                return false
            }
            index += 1
        }
        return true
    }
    public open override func toString(): String {
        return name()
    }
}

class BubbleSort <: BaseSorter {
    public override func name(): String {
        return "BubbleSort"
    }
    public override func sort(list: ArrayList<Int64>): ArrayList<Int64> {
        let result = copyInput(list)
        var end = result.size - 1
        while (end > 0) {
            var index = 0
            var swapped = false
            while (index < end) {
                if (result[index] > result[index + 1]) {
                    swap(result, index, index + 1)
                    swapped = true
                }
                index += 1
            }
            if (!swapped) {
                break
            }
            end -= 1
        }
        return result
    }
}

class InsertionSort <: BaseSorter {
    public override func name(): String {
        return "InsertionSort"
    }
    public override func sort(list: ArrayList<Int64>): ArrayList<Int64> {
        let result = copyInput(list)
        var index = 1
        while (index < result.size) {
            let value = result[index]
            var position = index - 1
            while ((position >= 0) && (result[position] > value)) {
                result[position + 1] = result[position]
                position -= 1
            }
            result[position + 1] = value
            index += 1
        }
        return result
    }
}

class SelectionSort <: BaseSorter {
    public override func name(): String {
        return "SelectionSort"
    }
    public override func sort(list: ArrayList<Int64>): ArrayList<Int64> {
        let result = copyInput(list)
        var index = 0
        while (index < result.size) {
            var minIndex = index
            var scan = index + 1
            while (scan < result.size) {
                if (result[scan] < result[minIndex]) {
                    minIndex = scan
                }
                scan += 1
            }
            if (minIndex != index) {
                swap(result, index, minIndex)
            }
            index += 1
        }
        return result
    }
}

class MergeSort <: BaseSorter {
    public override func name(): String {
        return "MergeSort"
    }
    public override func sort(list: ArrayList<Int64>): ArrayList<Int64> {
        let copied = copyInput(list)
        return mergeSort(copied)
    }
    func mergeSort(list: ArrayList<Int64>): ArrayList<Int64> {
        if (list.size <= 1) {
            return list
        }
        let middle = list.size / 2
        let left = ArrayList<Int64>()
        let right = ArrayList<Int64>()
        var index = 0
        while (index < middle) {
            left.add(list[index])
            index += 1
        }
        while (index < list.size) {
            right.add(list[index])
            index += 1
        }
        return merge(mergeSort(left), mergeSort(right))
    }
    func merge(left: ArrayList<Int64>, right: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        var leftIndex = 0
        var rightIndex = 0
        while ((leftIndex < left.size) && (rightIndex < right.size)) {
            if (left[leftIndex] <= right[rightIndex]) {
                result.add(left[leftIndex])
                leftIndex += 1
            } else {
                result.add(right[rightIndex])
                rightIndex += 1
            }
        }
        while (leftIndex < left.size) {
            result.add(left[leftIndex])
            leftIndex += 1
        }
        while (rightIndex < right.size) {
            result.add(right[rightIndex])
            rightIndex += 1
        }
        return result
    }
}

class QuickSort <: BaseSorter {
    public override func name(): String {
        return "QuickSort"
    }
    public override func sort(list: ArrayList<Int64>): ArrayList<Int64> {
        let result = copyInput(list)
        quickSort(result, 0, result.size - 1)
        return result
    }
    func quickSort(list: ArrayList<Int64>, low: Int64, high: Int64): Unit {
        if (low >= high) {
            return
        }
        let pivotIndex = partition(list, low, high)
        quickSort(list, low, pivotIndex - 1)
        quickSort(list, pivotIndex + 1, high)
    }
    func partition(list: ArrayList<Int64>, low: Int64, high: Int64): Int64 {
        let pivot = list[high]
        var smaller = low
        var scan = low
        while (scan < high) {
            if (list[scan] <= pivot) {
                swap(list, smaller, scan)
                smaller += 1
            }
            scan += 1
        }
        swap(list, smaller, high)
        return smaller
    }
}

class Stack<T> <: ToString {
    let items = ArrayList<T>()
    func push(value: T) {
        items.add(value)
    }
    func pushAll(values: ArrayList<T>) {
        for (value in values) {
            push(value)
        }
    }
    func pop(): ?T {
        if (items.isEmpty()) {
            return None
        }
        let lastIndex = items.size - 1
        let value = items[lastIndex]
        items.remove(at: lastIndex)
        return value
    }
    func peek(): ?T {
        if (items.isEmpty()) {
            return None
        }
        return items[items.size - 1]
    }
    func isEmpty(): Bool {
        return items.isEmpty()
    }
    func size(): Int64 {
        return items.size
    }
    func clear() {
        items.clear()
    }
    func contains(value: T): Bool {
        return items.contains(value)
    }
    func toArrayList(): ArrayList<T> {
        let copied = ArrayList<T>()
        for (item in items) {
            copied.add(item)
        }
        return copied
    }
    func reverseCopy(): ArrayList<T> {
        let copied = ArrayList<T>()
        var index = items.size - 1
        while (index >= 0) {
            copied.add(items[index])
            index -= 1
        }
        return copied
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Stack[")
        var index = 0
        while (index < items.size) {
            if (index > 0) {
                builder.append(", ")
            }
            builder.append(items[index])
            index += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

class SortScenario <: ToString {
    let name: String
    let values: ArrayList<Int64>
    init(name: String, values: ArrayList<Int64>) {
        this.name = name
        this.values = values
    }
    public func toString(): String {
        return "SortScenario(name=${this.name}, values=${this.values})"
    }
}

class DemoSection <: ToString & Equatable<DemoSection> {
    let _ordinal: Int64
    public let title: String
    init(_ordinal: Int64, title: String) {
        this._ordinal = _ordinal
        this.title = title
    }
    public static let LINKED_LIST = DemoSection(0, "LinkedList Demo")
    public static let STACK = DemoSection(1, "Stack Demo")
    public static let QUEUE = DemoSection(2, "Queue Demo")
    public static let BST = DemoSection(3, "BinarySearchTree Demo")
    public static let SORTING = DemoSection(4, "Sorting Demo")
    public static let GRAPH = DemoSection(5, "Graph Demo")
    public static let HASH_TABLE = DemoSection(6, "HashTable Demo")
    public static let PRIORITY_QUEUE = DemoSection(7, "PriorityQueue Demo")
    public static let SUMMARY = DemoSection(8, "Project Summary")
    public func toString(): String {
            if (this == DemoSection.LINKED_LIST) { return "LINKED_LIST" }
            if (this == DemoSection.STACK) { return "STACK" }
            if (this == DemoSection.QUEUE) { return "QUEUE" }
            if (this == DemoSection.BST) { return "BST" }
            if (this == DemoSection.SORTING) { return "SORTING" }
            if (this == DemoSection.GRAPH) { return "GRAPH" }
            if (this == DemoSection.HASH_TABLE) { return "HASH_TABLE" }
            if (this == DemoSection.PRIORITY_QUEUE) { return "PRIORITY_QUEUE" }
            if (this == DemoSection.SUMMARY) { return "SUMMARY" }
return "DemoSection(?)"
    }
    public operator func ==(rhs: DemoSection): Bool {
        return this._ordinal == rhs._ordinal
    }
    public operator func !=(rhs: DemoSection): Bool {
        return !(this == rhs)
    }
}

class DemoResult <: ToString {
    let section: String
    let checks: Int64
    init(section: String, checks: Int64) {
        this.section = section
        this.checks = checks
    }
    public func toString(): String {
        return "DemoResult(section=${this.section}, checks=${this.checks})"
    }
}

extend LinkedList<Int64> {
    func sumValues(): Int64 {
        var total = 0
        for (value in this.toArrayList()) {
            total += value
        }
        return total
    }
}

extend ArrayList<Int64> {
    func pipeJoined(): String {
        return String.join(collectArray<String>(this.iterator().map({e => e.toString()})), delimiter: " | ")
    }
}

func printSection(section: DemoSection) {
    println("")
    println("=== ${section.title} ===")
}

func demoLinkedList(): DemoResult {
    printSection(DemoSection.LINKED_LIST)
    let list = LinkedList<Int64>()
    println("Initial list: ${list}")
    println("Initially empty: ${list.isEmpty()}")
    list.addFirst(3)
    list.addFirst(2)
    list.addLast(5)
    list.addAt(2, 4)
    list.addAt(0, 1)
    println("After inserts: ${list}")
    println("Join with pipes: ${list.toArrayList().pipeJoined()}")
    println("Size after inserts: ${list.size()}")
    println("Contains 4: ${list.contains(4)}")
    println("Contains 9: ${list.contains(9)}")
    println("Find 5 -> ${list.find(5)?.value}")
    println("Index of 4: ${list.indexOf(4)}")
    println("Value at index 3: ${list.get(3)}")
    let replaced = list.set(3, 40)
    println("Set index 3 to 40: ${replaced}")
    println("After set: ${list}")
    println("List sum: ${list.sumValues()}")
    let removedFirst = list.removeFirst()
    let removedLast = list.removeLast()
    println("Removed first: ${removedFirst}")
    println("Removed last: ${removedLast}")
    println("After end removals: ${list}")
    let removedValue = list.remove(40)
    println("Removed value 40: ${removedValue}")
    println("After removing 40: ${list}")
    list.addLast(7)
    list.addLast(8)
    list.addAt(1, 9)
    println("After more inserts: ${list}")
    let removedAt = list.remove(at: 2)
    println("Removed at index 2: ${removedAt}")
    println("Before reverse: ${list}")
    list.reverse()
    println("After reverse: ${list}")
    println("As array list: ${list.toArrayList()}")
    let copied = list.copy()
    copied.addLast(99)
    println("Copied list changed: ${copied}")
    println("Original remains: ${list}")
    list.clear()
    println("After clear: ${list}")
    println("Size after clear: ${list.size()}")
    println("Empty after clear: ${list.isEmpty()}")
    return DemoResult(DemoSection.LINKED_LIST.title, 18)
}

func demoStack(): DemoResult {
    printSection(DemoSection.STACK)
    let stack = Stack<String>()
    println("Initial stack: ${stack}")
    println("Initially empty: ${stack.isEmpty()}")
    stack.push("red")
    stack.push("green")
    stack.push("blue")
    println("After pushes: ${stack}")
    println("Peek: ${stack.peek()}")
    println("Contains green: ${stack.contains("green")}")
    println("Contains black: ${stack.contains("black")}")
    let extra = ArrayList<String>()
    extra.add("white")
    extra.add("gold")
    stack.pushAll(extra)
    println("After pushAll: ${stack}")
    println("Reverse copy: ${stack.reverseCopy()}")
    println("Size: ${stack.size()}")
    println("Pop 1: ${stack.pop()}")
    println("Pop 2: ${stack.pop()}")
    println("Stack now: ${stack}")
    println("As array list: ${stack.toArrayList()}")
    println("Peek after pops: ${stack.peek()}")
    stack.clear()
    println("After clear: ${stack}")
    println("Empty after clear: ${stack.isEmpty()}")
    println("Pop on empty: ${stack.pop()}")
    return DemoResult(DemoSection.STACK.title, 12)
}

func demoQueue(): DemoResult {
    printSection(DemoSection.QUEUE)
    let queue = Queue<Int64>()
    println("Initial queue: ${queue}")
    println("Initially empty: ${queue.isEmpty()}")
    queue.enqueue(10)
    queue.enqueue(20)
    queue.enqueue(30)
    println("After enqueues: ${queue}")
    println("Peek: ${queue.peek()}")
    println("Contains 20: ${queue.contains(20)}")
    println("Contains 99: ${queue.contains(99)}")
    let more = ArrayList<Int64>()
    more.add(40)
    more.add(50)
    queue.enqueueAll(more)
    println("After enqueueAll: ${queue}")
    println("Dequeue 1: ${queue.dequeue()}")
    println("Dequeue 2: ${queue.dequeue()}")
    println("Queue now: ${queue}")
    queue.rotate()
    println("After rotate: ${queue}")
    println("As array list: ${queue.toArrayList()}")
    println("Size: ${queue.size()}")
    queue.clear()
    println("After clear: ${queue}")
    println("Empty after clear: ${queue.isEmpty()}")
    println("Dequeue on empty: ${queue.dequeue()}")
    return DemoResult(DemoSection.QUEUE.title, 11)
}

func demoBinarySearchTree(): DemoResult {
    printSection(DemoSection.BST)
    let tree = BinarySearchTree()
    let values = ArrayList<Int64>()
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

func printSortResult(sorter: BaseSorter, scenario: SortScenario) {
    let sorted = sorter.sort(scenario.values())
    println("${sorter.name()} on ${scenario.name}: ${sorted}")
    println("${sorter.name()} sorted check: ${sorter.isSorted(sorted)}")
}

func demoSorting(): DemoResult {
    printSection(DemoSection.SORTING)
    let scenarioAValues = ArrayList<Int64>()
    scenarioAValues.add(9)
    scenarioAValues.add(4)
    scenarioAValues.add(7)
    scenarioAValues.add(1)
    scenarioAValues.add(3)
    scenarioAValues.add(8)
    scenarioAValues.add(2)
    let scenarioA = SortScenario("scenarioA", scenarioAValues)
    let scenarioBValues = ArrayList<Int64>()
    scenarioBValues.add(5)
    scenarioBValues.add(1)
    scenarioBValues.add(5)
    scenarioBValues.add(2)
    scenarioBValues.add(9)
    scenarioBValues.add(2)
    scenarioBValues.add(0)
    let scenarioB = SortScenario("scenarioB", scenarioBValues)
    println("Original scenarioA: ${scenarioA.values()}")
    println("Original scenarioB: ${scenarioB.values()}")
    let bubble = BubbleSort()
    let insertion = InsertionSort()
    let selection = SelectionSort()
    let merge = MergeSort()
    let quick = QuickSort()
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
    println("ScenarioA unchanged: ${scenarioA.values()}")
    println("ScenarioB unchanged: ${scenarioB.values()}")
    return DemoResult(DemoSection.SORTING.title, 12)
}

func demoGraph(): DemoResult {
    printSection(DemoSection.GRAPH)
    let graph = Graph()
    graph.addEdge("A", "B")
    graph.addEdge("A", "C")
    graph.addEdge("B", "D")
    graph.addEdge("B", "E")
    graph.addEdge("C", "F")
    graph.addEdge("E", "G")
    graph.addEdge("F", "G")
    graph.addVertex("H")
    println("Graph structure:\n${graph}")
    println("Vertices sorted: ${({ => let _s = collectArrayList(graph.vertices().iterator()); sort(_s, stable: true); _s })()}")
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
    println("Vertices sorted after removal: ${({ => let _s = collectArrayList(graph.vertices().iterator()); sort(_s, stable: true); _s })()}")
    println("Edge count after removal: ${graph.getEdgeCount()}")
    return DemoResult(DemoSection.GRAPH.title, 18)
}

func demoHashTable(): DemoResult {
    printSection(DemoSection.HASH_TABLE)
    let table = HashTable<Int64>(5)
    println("Initially empty: ${table.isEmpty()}")
    table.put("ab", 10)
    table.put("ba", 20)
    table.put("cab", 30)
    table.put("dog", 40)
    table.put("god", 50)
    println("Table after inserts: ${table}")
    println("Size: ${table.size()}")
    println("Get ab: ${table.get("ab")}")
    println("Get ba: ${table.get("ba")}")
    println("Get missing: ${table.get("missing")}")
    println("Contains cab: ${table.contains("cab")}")
    println("Contains cat: ${table.contains("cat")}")
    println("Bucket 0: ${table.bucketView(0)}")
    println("Bucket 3: ${table.bucketView(3)}")
    println("Keys sorted: ${({ => let _s = collectArrayList(table.keys()().iterator()); sort(_s, stable: true); _s })()}")
    println("Values sorted: ${({ => let _s = collectArrayList(table.values()().iterator()); sort(_s, stable: true); _s })()}")
    println("Load factor: ${table.loadFactor()}")
    println("Update ba old value: ${table.put("ba", 22)}")
    println("Table after update: ${table}")
    println("Remove cab: ${table.remove("cab")}")
    println("Remove missing: ${table.remove("missing")}")
    println("Table after removals: ${table}")
    println("Entries snapshot size: ${table.entries().size}")
    table.clear()
    println("After clear size: ${table.size()}")
    println("After clear empty: ${table.isEmpty()}")
    return DemoResult(DemoSection.HASH_TABLE.title, 16)
}

func demoPriorityQueue(): DemoResult {
    printSection(DemoSection.PRIORITY_QUEUE)
    let queue = PriorityQueue()
    println("Initially empty: ${queue.isEmpty()}")
    queue.enqueue(9)
    queue.enqueue(4)
    queue.enqueue(7)
    queue.enqueue(1)
    queue.enqueue(6)
    queue.enqueue(2)
    println("Queue after enqueues: ${queue}")
    println("Peek: ${queue.peek()}")
    println("Contains 7: ${queue.contains(7)}")
    println("Contains 99: ${queue.contains(99)}")
    println("Validate heap: ${queue.validateHeap()}")
    println("Array view: ${queue.toArrayList()}")
    println("Dequeue 1: ${queue.dequeue()}")
    println("Dequeue 2: ${queue.dequeue()}")
    println("Queue after dequeues: ${queue}")
    println("Peek after dequeues: ${queue.peek()}")
    println("Validate heap after dequeues: ${queue.validateHeap()}")
    let fromListValues = ArrayList<Int64>()
    fromListValues.add(12)
    fromListValues.add(3)
    fromListValues.add(17)
    fromListValues.add(8)
    fromListValues.add(5)
    let built = PriorityQueue.fromList(fromListValues)
    println("Built from list: ${built}")
    println("Built queue peek: ${built.peek()}")
    println("Built queue validate: ${built.validateHeap()}")
    println("Built queue dequeue: ${built.dequeue()}")
    println("Built queue after dequeue: ${built}")
    queue.clear()
    println("After clear empty: ${queue.isEmpty()}")
    return DemoResult(DemoSection.PRIORITY_QUEUE.title, 14)
}

func demoSummary(results: ArrayList<DemoResult>) {
    printSection(DemoSection.SUMMARY)
    var totalChecks = 0
    for (result in results) {
        println("${result.section}: ${result.checks} checks")
        totalChecks += result.checks
    }
    println("Total sections: ${results.size}")
    println("Total checks: ${totalChecks}")
}

main() {
    println("Kotlin DSA Project Demo")
    println("Deterministic data structures and algorithms output")
    let results = ArrayList<DemoResult>()
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
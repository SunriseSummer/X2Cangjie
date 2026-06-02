package proj_queue

import std.collection.*

class Queue {
    let data = ArrayList<Int64>()
    func enqueue(value: Int64) {
        data.add(value)
    }
    func dequeue(): Int64 {
        if (data.isEmpty()) {
            throw Exception("Queue is empty")
        }
        let value = data[0]
        data.remove(at: 0)
        return value
    }
    func peek(): Int64 {
        if (data.isEmpty()) {
            throw Exception("Queue is empty")
        }
        return data[0]
    }
    func isEmpty(): Bool {
        return data.isEmpty()
    }
    func size(): Int64 {
        return data.size
    }
    func printQueue() {
        let sb = StringBuilder()
        sb.append("Queue[")
        for (i in 0..data.size) {
            if (i > 0) {
                sb.append(", ")
            }
            sb.append(data[i])
        }
        sb.append("]")
        println(sb.toString())
    }
}

class Stack {
    let data = ArrayList<Int64>()
    func push(value: Int64) {
        data.add(value)
    }
    func pop(): Int64 {
        if (data.isEmpty()) {
            throw Exception("Stack is empty")
        }
        let value = data[data.size - 1]
        data.remove(at: data.size - 1)
        return value
    }
    func peek(): Int64 {
        if (data.isEmpty()) {
            throw Exception("Stack is empty")
        }
        return data[data.size - 1]
    }
    func isEmpty(): Bool {
        return data.isEmpty()
    }
    func size(): Int64 {
        return data.size
    }
    func printStack() {
        let sb = StringBuilder()
        sb.append("Stack[")
        for (i in 0..data.size) {
            if (i > 0) {
                sb.append(", ")
            }
            sb.append(data[i])
        }
        sb.append("]")
        println(sb.toString())
    }
}

main() {
    println("=== Queue Demo ===")
    let q = Queue()
    q.enqueue(10)
    q.enqueue(20)
    q.enqueue(30)
    q.printQueue()
    println("Peek: ${q.peek()}")
    println("Dequeue: ${q.dequeue()}")
    println("Dequeue: ${q.dequeue()}")
    q.printQueue()
    q.enqueue(40)
    q.enqueue(50)
    q.printQueue()
    println("Size: ${q.size()}")
    println("\n=== Stack Demo ===")
    let s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    s.printStack()
    println("Peek: ${s.peek()}")
    println("Pop: ${s.pop()}")
    println("Pop: ${s.pop()}")
    s.printStack()
    s.push(4)
    s.push(5)
    s.printStack()
    println("Size: ${s.size()}")
    println("\n=== Error Handling ===")
    let eq = Queue()
    try {
        let v = eq.dequeue()
        println("Got: ${v}")
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
    let es = Stack()
    try {
        let v = es.pop()
        println("Got: ${v}")
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
}
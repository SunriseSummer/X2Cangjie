import std.collection.*

class IntStack <: ToString {
    let data = ArrayList<Int64>()
    func push(v: Int64) {
        data.add(v)
    }
    func pop(): Int64 {
        let v = data[data.size - 1]
        data.remove(at: data.size - 1)
        return v
    }
    func peek(): Int64 {
        return data[data.size - 1]
    }
    func isEmpty(): Bool {
        return data.isEmpty()
    }
    func size(): Int64 {
        return data.size
    }
    public override func toString(): String {
        return "Stack${data}"
    }
}

class IntQueue <: ToString {
    let data = ArrayList<Int64>()
    func enqueue(v: Int64) {
        data.add(v)
    }
    func dequeue(): Int64 {
        let v = data[0]
        data.remove(at: 0)
        return v
    }
    func front(): Int64 {
        return data[0]
    }
    func isEmpty(): Bool {
        return data.isEmpty()
    }
    func size(): Int64 {
        return data.size
    }
    public override func toString(): String {
        return "Queue${data}"
    }
}

main() {
    let stack = IntStack()
    for (i in 1..=5) {
        stack.push(i)
    }
    println(stack)
    println("Peek: ${stack.peek()}")
    println("Pop: ${stack.pop()}")
    println("Pop: ${stack.pop()}")
    println("Size: ${stack.size()}")
    println(stack)
    let queue = IntQueue()
    for (i in 10..=14) {
        queue.enqueue(i)
    }
    println(queue)
    println("Front: ${queue.front()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Size: ${queue.size()}")
    println(queue)
    let reverser = IntStack()
    for (i in 1..=5) {
        reverser.push(i)
    }
    let reversed = ArrayList<Int64>()
    while (!reverser.isEmpty()) {
        reversed.add(reverser.pop())
    }
    println("Reversed: ${String.join(collectArray<String>(reversed.iterator().map({e => e.toString()})), delimiter: " ")}")
}

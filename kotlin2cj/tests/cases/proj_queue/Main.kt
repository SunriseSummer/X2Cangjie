fun main() {
    println("=== Queue Demo ===")
    val q = Queue()
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
    val s = Stack()
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
    val eq = Queue()
    try {
        val v = eq.dequeue()
        println("Got: $v")
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
    val es = Stack()
    try {
        val v = es.pop()
        println("Got: $v")
    } catch (e: Exception) {
        println("Caught: ${e.message}")
    }
}

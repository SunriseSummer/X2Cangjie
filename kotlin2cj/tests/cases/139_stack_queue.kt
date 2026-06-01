// Stack and Queue implementations using ArrayList
class IntStack {
    private val data = ArrayList<Int>()

    fun push(v: Int) { data.add(v) }

    fun pop(): Int {
        val v = data[data.size - 1]
        data.removeAt(data.size - 1)
        return v
    }

    fun peek(): Int = data[data.size - 1]
    fun isEmpty(): Boolean = data.isEmpty()
    fun size(): Int = data.size

    override fun toString(): String {
        return "Stack${data}"
    }
}

class IntQueue {
    private val data = ArrayList<Int>()

    fun enqueue(v: Int) { data.add(v) }

    fun dequeue(): Int {
        val v = data[0]
        data.removeAt(0)
        return v
    }

    fun front(): Int = data[0]
    fun isEmpty(): Boolean = data.isEmpty()
    fun size(): Int = data.size

    override fun toString(): String {
        return "Queue${data}"
    }
}

fun main() {
    // Stack operations
    val stack = IntStack()
    for (i in 1..5) stack.push(i)
    println(stack)
    println("Peek: ${stack.peek()}")
    println("Pop: ${stack.pop()}")
    println("Pop: ${stack.pop()}")
    println("Size: ${stack.size()}")
    println(stack)

    // Queue operations
    val queue = IntQueue()
    for (i in 10..14) queue.enqueue(i)
    println(queue)
    println("Front: ${queue.front()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Dequeue: ${queue.dequeue()}")
    println("Size: ${queue.size()}")
    println(queue)

    // Use stack to reverse a sequence
    val reverser = IntStack()
    for (i in 1..5) reverser.push(i)
    val reversed = ArrayList<Int>()
    while (!reverser.isEmpty()) {
        reversed.add(reverser.pop())
    }
    println("Reversed: ${reversed.joinToString(" ")}")
}

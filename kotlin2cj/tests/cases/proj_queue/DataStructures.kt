class Queue {
    val data = mutableListOf<Int>()

    fun enqueue(value: Int) {
        data.add(value)
    }

    fun dequeue(): Int {
        if (data.isEmpty()) {
            throw Exception("Queue is empty")
        }
        val value = data[0]
        data.removeAt(0)
        return value
    }

    fun peek(): Int {
        if (data.isEmpty()) {
            throw Exception("Queue is empty")
        }
        return data[0]
    }

    fun isEmpty(): Boolean = data.isEmpty()
    fun size(): Int = data.size

    fun printQueue() {
        val sb = StringBuilder()
        sb.append("Queue[")
        for (i in 0 until data.size) {
            if (i > 0) sb.append(", ")
            sb.append(data[i])
        }
        sb.append("]")
        println(sb.toString())
    }
}

class Stack {
    val data = mutableListOf<Int>()

    fun push(value: Int) {
        data.add(value)
    }

    fun pop(): Int {
        if (data.isEmpty()) {
            throw Exception("Stack is empty")
        }
        val value = data[data.size - 1]
        data.removeAt(data.size - 1)
        return value
    }

    fun peek(): Int {
        if (data.isEmpty()) {
            throw Exception("Stack is empty")
        }
        return data[data.size - 1]
    }

    fun isEmpty(): Boolean = data.isEmpty()
    fun size(): Int = data.size

    fun printStack() {
        val sb = StringBuilder()
        sb.append("Stack[")
        for (i in 0 until data.size) {
            if (i > 0) sb.append(", ")
            sb.append(data[i])
        }
        sb.append("]")
        println(sb.toString())
    }
}

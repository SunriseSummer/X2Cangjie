class IntQueue {
    private val items = ArrayList<Long>()
    private var head: Int = 0

    fun enqueue(value: Long) {
        items.add(value)
    }

    fun dequeue(): Long {
        val value = items[head]
        head++
        return value
    }

    fun peek(): Long {
        return items[head]
    }

    fun isEmpty(): Boolean {
        return head >= items.size
    }

    fun size(): Int {
        return items.size - head
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("Queue[")
        var i = head
        var first = true
        while (i < items.size) {
            if (!first) builder.append(", ")
            builder.append(items[i].toString())
            first = false
            i++
        }
        builder.append("]")
        return builder.toString()
    }
}

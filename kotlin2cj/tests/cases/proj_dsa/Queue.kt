class Queue<T> {
    private val items = ArrayList<T>()

    fun enqueue(value: T) {
        items.add(value)
    }

    fun enqueueAll(values: ArrayList<T>) {
        for (value in values) {
            enqueue(value)
        }
    }

    fun dequeue(): T? {
        if (items.isEmpty()) {
            return null
        }
        val value = items[0]
        items.removeAt(0)
        return value
    }

    fun peek(): T? {
        if (items.isEmpty()) {
            return null
        }
        return items[0]
    }

    fun isEmpty(): Boolean {
        return items.isEmpty()
    }

    fun size(): Int {
        return items.size
    }

    fun clear() {
        items.clear()
    }

    fun contains(value: T): Boolean {
        return items.contains(value)
    }

    fun rotate() {
        if (items.size <= 1) {
            return
        }
        val front = dequeue()
        if (front != null) {
            enqueue(front)
        }
    }

    fun toArrayList(): ArrayList<T> {
        val copied = ArrayList<T>()
        for (item in items) {
            copied.add(item)
        }
        return copied
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("Queue[")
        var index = 0
        while (index < items.size) {
            if (index > 0) {
                builder.append(", ")
            }
            builder.append(items[index])
            index++
        }
        builder.append("]")
        return builder.toString()
    }
}

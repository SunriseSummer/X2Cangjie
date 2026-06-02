class Stack<T> {
    private val items = ArrayList<T>()

    fun push(value: T) {
        items.add(value)
    }

    fun pushAll(values: ArrayList<T>) {
        for (value in values) {
            push(value)
        }
    }

    fun pop(): T? {
        if (items.isEmpty()) {
            return null
        }
        val lastIndex = items.size - 1
        val value = items[lastIndex]
        items.removeAt(lastIndex)
        return value
    }

    fun peek(): T? {
        if (items.isEmpty()) {
            return null
        }
        return items[items.size - 1]
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

    fun toArrayList(): ArrayList<T> {
        val copied = ArrayList<T>()
        for (item in items) {
            copied.add(item)
        }
        return copied
    }

    fun reverseCopy(): ArrayList<T> {
        val copied = ArrayList<T>()
        var index = items.size - 1
        while (index >= 0) {
            copied.add(items[index])
            index--
        }
        return copied
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("Stack[")
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

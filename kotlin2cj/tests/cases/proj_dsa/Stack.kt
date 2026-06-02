class IntStack {
    private val items = ArrayList<Long>()

    fun push(value: Long) {
        items.add(value)
    }

    fun pop(): Long {
        val last = items[items.size - 1]
        items.removeAt(items.size - 1)
        return last
    }

    fun peek(): Long {
        return items[items.size - 1]
    }

    fun isEmpty(): Boolean {
        return items.size == 0
    }

    fun size(): Int {
        return items.size
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("Stack[")
        var i = 0
        while (i < items.size) {
            if (i > 0) builder.append(", ")
            builder.append(items[i].toString())
            i++
        }
        builder.append("]")
        return builder.toString()
    }
}

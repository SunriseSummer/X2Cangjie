class MinHeap {
    private val data = ArrayList<Long>()

    fun insert(value: Long) {
        data.add(value)
        siftUp(data.size - 1)
    }

    fun extractMin(): Long {
        val min = data[0]
        val last = data[data.size - 1]
        data.removeAt(data.size - 1)
        if (data.size > 0) {
            data[0] = last
            siftDown(0)
        }
        return min
    }

    fun peek(): Long {
        return data[0]
    }

    fun isEmpty(): Boolean {
        return data.size == 0
    }

    fun size(): Int {
        return data.size
    }

    private fun siftUp(index: Int) {
        var i = index
        while (i > 0) {
            val parent = (i - 1) / 2
            if (data[i] < data[parent]) {
                val temp = data[i]
                data[i] = data[parent]
                data[parent] = temp
                i = parent
            } else {
                break
            }
        }
    }

    private fun siftDown(index: Int) {
        var i = index
        while (true) {
            var smallest = i
            val left = 2 * i + 1
            val right = 2 * i + 2
            if (left < data.size && data[left] < data[smallest]) {
                smallest = left
            }
            if (right < data.size && data[right] < data[smallest]) {
                smallest = right
            }
            if (smallest != i) {
                val temp = data[i]
                data[i] = data[smallest]
                data[smallest] = temp
                i = smallest
            } else {
                break
            }
        }
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("Heap[")
        var i = 0
        while (i < data.size) {
            if (i > 0) builder.append(", ")
            builder.append(data[i].toString())
            i++
        }
        builder.append("]")
        return builder.toString()
    }
}

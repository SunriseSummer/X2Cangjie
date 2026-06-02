class PriorityQueue {
    private val heap = ArrayList<Int>()

    companion object {
        fun fromList(values: ArrayList<Int>): PriorityQueue {
            val queue = PriorityQueue()
            queue.buildFrom(values)
            return queue
        }
    }

    fun enqueue(value: Int) {
        heap.add(value)
        bubbleUp(heap.size - 1)
    }

    fun dequeue(): Int? {
        if (heap.isEmpty()) {
            return null
        }
        if (heap.size == 1) {
            return heap.removeAt(0)
        }

        val value = heap[0]
        val last = heap.removeAt(heap.size - 1)
        heap[0] = last
        bubbleDown(0)
        return value
    }

    fun peek(): Int? {
        if (heap.isEmpty()) {
            return null
        }
        return heap[0]
    }

    fun isEmpty(): Boolean {
        return heap.isEmpty()
    }

    fun size(): Int {
        return heap.size
    }

    fun clear() {
        heap.clear()
    }

    fun contains(value: Int): Boolean {
        return heap.contains(value)
    }

    fun buildFrom(values: ArrayList<Int>) {
        clear()
        for (value in values) {
            heap.add(value)
        }
        var index = parentIndex(heap.size - 1)
        while (index >= 0) {
            bubbleDown(index)
            index--
        }
    }

    private fun parentIndex(index: Int): Int {
        return (index - 1) / 2
    }

    private fun leftChildIndex(index: Int): Int {
        return index * 2 + 1
    }

    private fun rightChildIndex(index: Int): Int {
        return index * 2 + 2
    }

    private fun bubbleUp(startIndex: Int) {
        var index = startIndex
        while (index > 0) {
            val parent = parentIndex(index)
            if (heap[parent] <= heap[index]) {
                break
            }
            swap(parent, index)
            index = parent
        }
    }

    private fun bubbleDown(startIndex: Int) {
        var index = startIndex
        while (true) {
            val left = leftChildIndex(index)
            val right = rightChildIndex(index)
            var smallest = index

            if (left < heap.size && heap[left] < heap[smallest]) {
                smallest = left
            }
            if (right < heap.size && heap[right] < heap[smallest]) {
                smallest = right
            }
            if (smallest == index) {
                break
            }
            swap(index, smallest)
            index = smallest
        }
    }

    private fun swap(first: Int, second: Int) {
        val temp = heap[first]
        heap[first] = heap[second]
        heap[second] = temp
    }

    fun validateHeap(): Boolean {
        var index = 0
        while (index < heap.size) {
            val left = leftChildIndex(index)
            val right = rightChildIndex(index)
            if (left < heap.size && heap[index] > heap[left]) {
                return false
            }
            if (right < heap.size && heap[index] > heap[right]) {
                return false
            }
            index++
        }
        return true
    }

    fun toArrayList(): ArrayList<Int> {
        val copied = ArrayList<Int>()
        for (value in heap) {
            copied.add(value)
        }
        return copied
    }

    override fun toString(): String {
        return "PriorityQueue${heap}"
    }
}

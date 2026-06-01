// Min-heap (priority queue) implementation
class MinHeap {
    private val data = ArrayList<Int>()

    fun size(): Int = data.size
    fun isEmpty(): Boolean = data.isEmpty()

    fun insert(value: Int) {
        data.add(value)
        siftUp(data.size - 1)
    }

    fun extractMin(): Int {
        val min = data[0]
        val last = data[data.size - 1]
        data.removeAt(data.size - 1)
        if (data.isNotEmpty()) {
            data[0] = last
            siftDown(0)
        }
        return min
    }

    fun peek(): Int = data[0]

    private fun siftUp(idx: Int) {
        var i = idx
        while (i > 0) {
            val parent = (i - 1) / 2
            if (data[i] < data[parent]) {
                val tmp = data[i]
                data[i] = data[parent]
                data[parent] = tmp
                i = parent
            } else {
                break
            }
        }
    }

    private fun siftDown(idx: Int) {
        var i = idx
        val n = data.size
        while (true) {
            var smallest = i
            val left = 2 * i + 1
            val right = 2 * i + 2
            if (left < n && data[left] < data[smallest]) {
                smallest = left
            }
            if (right < n && data[right] < data[smallest]) {
                smallest = right
            }
            if (smallest != i) {
                val tmp = data[i]
                data[i] = data[smallest]
                data[smallest] = tmp
                i = smallest
            } else {
                break
            }
        }
    }
}

fun heapSort(arr: ArrayList<Int>): ArrayList<Int> {
    val heap = MinHeap()
    for (v in arr) {
        heap.insert(v)
    }
    val result = ArrayList<Int>()
    while (!heap.isEmpty()) {
        result.add(heap.extractMin())
    }
    return result
}

fun main() {
    val heap = MinHeap()
    for (v in arrayListOf(5, 3, 8, 1, 9, 2, 7)) {
        heap.insert(v)
    }
    println("Min: ${heap.peek()}")
    println("Size: ${heap.size()}")

    val extracted = ArrayList<Int>()
    while (!heap.isEmpty()) {
        extracted.add(heap.extractMin())
    }
    println("Extracted: ${extracted.joinToString(" ")}")

    // Heap sort
    val sorted = heapSort(arrayListOf(42, 15, 3, 87, 1, 23, 56))
    println("Sorted: ${sorted.joinToString(" ")}")
}

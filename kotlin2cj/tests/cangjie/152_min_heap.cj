import std.collection.*

class MinHeap {
    let data = ArrayList<Int64>()
    func size(): Int64 {
        return data.size
    }
    func isEmpty(): Bool {
        return data.isEmpty()
    }
    func insert(value: Int64) {
        data.add(value)
        siftUp(data.size - 1)
    }
    func extractMin(): Int64 {
        let min = data[0]
        let last = data[data.size - 1]
        data.remove(at: data.size - 1)
        if (!(data.isEmpty())) {
            data[0] = last
            siftDown(0)
        }
        return min
    }
    func peek(): Int64 {
        return data[0]
    }
    func siftUp(idx: Int64) {
        var i = idx
        while (i > 0) {
            let parent = (i - 1) / 2
            if (data[i] < data[parent]) {
                let tmp = data[i]
                data[i] = data[parent]
                data[parent] = tmp
                i = parent
            } else {
                break
            }
        }
    }
    func siftDown(idx: Int64) {
        var i = idx
        let n = data.size
        while (true) {
            var smallest = i
            let left = (2 * i) + 1
            let right = (2 * i) + 2
            if ((left < n) && (data[left] < data[smallest])) {
                smallest = left
            }
            if ((right < n) && (data[right] < data[smallest])) {
                smallest = right
            }
            if (smallest != i) {
                let tmp = data[i]
                data[i] = data[smallest]
                data[smallest] = tmp
                i = smallest
            } else {
                break
            }
        }
    }
}

func heapSort(arr: ArrayList<Int64>): ArrayList<Int64> {
    let heap = MinHeap()
    for (v in arr) {
        heap.insert(v)
    }
    let result = ArrayList<Int64>()
    while (!heap.isEmpty()) {
        result.add(heap.extractMin())
    }
    return result
}

main() {
    let heap = MinHeap()
    for (v in ArrayList([5, 3, 8, 1, 9, 2, 7])) {
        heap.insert(v)
    }
    println("Min: ${heap.peek()}")
    println("Size: ${heap.size()}")
    let extracted = ArrayList<Int64>()
    while (!heap.isEmpty()) {
        extracted.add(heap.extractMin())
    }
    println("Extracted: ${String.join(collectArray<String>(extracted.iterator().map({e => e.toString()})), delimiter: " ")}")
    let sorted = heapSort(ArrayList([42, 15, 3, 87, 1, 23, 56]))
    println("Sorted: ${String.join(collectArray<String>(sorted.iterator().map({e => e.toString()})), delimiter: " ")}")
}

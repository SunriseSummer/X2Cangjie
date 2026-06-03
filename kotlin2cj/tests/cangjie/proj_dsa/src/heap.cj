package proj_dsa

import std.collection.*

class MinHeap <: ToString {
    let data = ArrayList<Int64>()
    func insert(value: Int64) {
        data.add(value)
        siftUp(data.size - 1)
    }
    func extractMin(): Int64 {
        let min = data[0]
        let last = data[data.size - 1]
        data.remove(at: data.size - 1)
        if (data.size > 0) {
            data[0] = last
            siftDown(0)
        }
        return min
    }
    func peek(): Int64 {
        return data[0]
    }
    func isEmpty(): Bool {
        return data.size == 0
    }
    func size(): Int64 {
        return data.size
    }
    func siftUp(index: Int64) {
        var i = index
        while (i > 0) {
            let parent = (i - 1) / 2
            if (data[i] < data[parent]) {
                let temp = data[i]
                data[i] = data[parent]
                data[parent] = temp
                i = parent
            } else {
                break
            }
        }
    }
    func siftDown(index: Int64) {
        var i = index
        while (true) {
            var smallest = i
            let left = (2 * i) + 1
            let right = (2 * i) + 2
            if ((left < data.size) && (data[left] < data[smallest])) {
                smallest = left
            }
            if ((right < data.size) && (data[right] < data[smallest])) {
                smallest = right
            }
            if (smallest != i) {
                let temp = data[i]
                data[i] = data[smallest]
                data[smallest] = temp
                i = smallest
            } else {
                break
            }
        }
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Heap[")
        var i = 0
        while (i < data.size) {
            if (i > 0) {
                builder.append(", ")
            }
            builder.append(data[i].toString())
            i += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

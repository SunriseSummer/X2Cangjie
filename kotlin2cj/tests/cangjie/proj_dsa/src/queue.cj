package proj_dsa

import std.collection.*

class IntQueue <: ToString {
    let items = ArrayList<Int64>()
    var head: Int64 = 0
    func enqueue(value: Int64) {
        items.add(value)
    }
    func dequeue(): Int64 {
        let value = items[head]
        head += 1
        return value
    }
    func peek(): Int64 {
        return items[head]
    }
    func isEmpty(): Bool {
        return head >= items.size
    }
    func size(): Int64 {
        return items.size - head
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Queue[")
        var i = head
        var first = true
        while (i < items.size) {
            if (!first) {
                builder.append(", ")
            }
            builder.append(items[i].toString())
            first = false
            i += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

package proj_dsa

import std.collection.*

class IntStack <: ToString {
    let items = ArrayList<Int64>()
    func push(value: Int64) {
        items.add(value)
    }
    func pop(): Int64 {
        let last = items[items.size - 1]
        items.remove(at: items.size - 1)
        return last
    }
    func peek(): Int64 {
        return items[items.size - 1]
    }
    func isEmpty(): Bool {
        return items.size == 0
    }
    func size(): Int64 {
        return items.size
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("Stack[")
        var i = 0
        while (i < items.size) {
            if (i > 0) {
                builder.append(", ")
            }
            builder.append(items[i].toString())
            i += 1
        }
        builder.append("]")
        return builder.toString()
    }
}

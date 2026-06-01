import std.collection.*

class IntStack {
    let items = ArrayList<Int64>()
    func push(x: Int64) {
        items.add(x)
    }
    func size(): Int64 {
        return items.size
    }
    func top(): Int64 {
        return items[items.size - 1]
    }
}

main() {
    let s = IntStack()
    s.push(10)
    s.push(20)
    s.push(30)
    println("size=${s.size()} top=${s.top()}")
}

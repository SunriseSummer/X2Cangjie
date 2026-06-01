import std.collection.*

class IntStack {
    let items = ArrayList<Int64>()
    func push(x: Int64) {
        items.add(x)
    }
    func pop(): Int64 {
        let top = items[items.size - 1]
        items.remove(at: items.size - 1)
        return top
    }
    func isEmpty(): Bool {
        return items.isEmpty()
    }
    func size(): Int64 {
        return items.size
    }
}

main() {
    let st = IntStack()
    for (i in 1..=5) {
        st.push(i * i)
    }
    println(st.size())
    var sum = 0
    while (!st.isEmpty()) {
        sum = sum + st.pop()
    }
    println(sum)
}

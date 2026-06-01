import std.collection.*

class Counter {
    var value: Int64
    init(value: Int64) {
        this.value = value
    }
    func inc() {
        value += 1
    }
}

main() {
    let counters = ArrayList([Counter(0), Counter(10), Counter(20)])
    for (c in counters) {
        c.inc()
        c.inc()
    }
    var total = 0
    for (c in counters) {
        total += c.value
    }
    println("total=${total}")
}

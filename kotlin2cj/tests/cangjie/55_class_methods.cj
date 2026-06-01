class Counter {
    var value: Int64
    init(value: Int64) {
        this.value = value
    }
    func inc() {
        value += 1
    }
    func add(n: Int64) {
        value += n
    }
    func isEven(): Bool {
        return (value % 2) == 0
    }
}

main() {
    let c = Counter(0)
    c.inc()
    c.inc()
    c.add(5)
    println("value=${c.value}")
    println("even=${c.isEven()}")
    c.inc()
    println("even=${c.isEven()}")
}

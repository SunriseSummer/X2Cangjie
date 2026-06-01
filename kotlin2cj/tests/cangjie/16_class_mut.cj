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
}

main() {
    let c = Counter(0)
    c.inc()
    c.inc()
    c.add(10)
    println("value=${c.value}")
}

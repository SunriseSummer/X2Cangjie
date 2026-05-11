open class Counter {
    var value: Int64 = 0
    init(start: Int64) {
        this.value = start
    }
    public open func inc(): Unit {
        this.value = this.value + 1
    }
    public open func get(): Int64 {
        return this.value
    }
}

let c = Counter(10)

main() {
    c.inc()
    c.inc()
    c.inc()
    println("value=${c.get()}")
    return 0
}

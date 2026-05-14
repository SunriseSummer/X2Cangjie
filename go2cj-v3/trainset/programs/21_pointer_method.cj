open class Counter {
    public var count: Int64
    public init() {
        this.count = 0
    }
    public func Inc(): Unit {
        this.count++
    }
    public func Get(): Int64 {
        return this.count
    }
}

main() {
    let c = Counter()
    for (i in 0..5) {
        c.Inc()
    }
    println(c.Get())
    c.Inc()
    c.Inc()
    println(c.Get())
    return 0
}

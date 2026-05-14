open class Counter {
    public var count: Int64
    public init(count: Int64) {
        this.count = count
    }
    public func Inc(): Unit {
        this.count++
    }
    public func Get(): Int64 {
        return this.count
    }
}

main() {
    var c = Counter(0)
    for (_ in 0..5) {
        c.Inc()
    }
    println(c.Get())
    return 0
}
